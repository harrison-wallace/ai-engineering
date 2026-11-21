#!/usr/bin/env python3
"""Write a draw-infra spec as an editable draw.io file, and export it to PNG with the draw.io CLI.

The layout is the one diagram.py computes, so the .drawio matches the page box for box. Each
boundary is a draw.io container (moving it moves its parts). Edges keep their checked routes
as waypoints. A spec with modes gets one draw.io page per mode. A part with an `icon` gets the
AWS icon inside its box.

Icon names, colours, the broken-icon list, and the group styles come from Alexey Vidanov's
aws-architecture-diagram skill (MIT).

Used through diagram.py: `diagram.py drawio <spec.json> <out.drawio> [--png <out.png>]`.
"""
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from html import escape

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
from diagram import (BOX_H, BOX_W, boundary_rects, in_modes, label_spots, modes_of, placed,  # noqa: E402
                     segments, val)

FG, MUTED, ACCENT, SOFT, RED = "#232F3E", "#7D8998", "#2457D6", "#DAE8FC", "#B85450"
TOP = 30  # room for the title

# Service icons (resourceIcon, white glyph on a coloured square), by draw.io resIcon name.
_SVC = {
    "#ED7100": "ec2 lambda fargate ecs eks ecr elastic_beanstalk lightsail batch app_runner",
    "#C925D1": "aurora dynamodb elasticache neptune rds timestream documentdb_with_mongodb_compatibility "
               "xray codepipeline codebuild codecommit codedeploy",
    "#7AA116": "s3 elastic_block_store elastic_file_system fsx glacier backup iot_core",
    "#8C4FFF": "cloudfront route_53 elastic_load_balancing vpc_privatelink direct_connect global_accelerator "
               "transit_gateway redshift elasticsearch_service managed_streaming_for_kafka kinesis "
               "kinesis_data_firehose athena glue quicksight emr lake_formation",
    "#E7157B": "api_gateway sns sqs eventbridge step_functions appsync mq cloudwatch_2 systems_manager "
               "cloudtrail cloudformation config organizations managed_workflows_for_apache_airflow",
    "#DD344C": "cognito guardduty key_management_service secrets_manager waf single_sign_on "
               "certificate_manager_3 network_firewall shield simple_email_service",
    "#01A88D": "bedrock sagemaker comprehend textract transcribe polly translate lex",
}
ICONS = {name: ("svc", colour) for colour, names in _SVC.items() for name in names.split()}
# Resource icons (a standalone shape, no frame).
ICONS.update({n: ("res", "#8C4FFF") for n in
              "nat_gateway internet_gateway application_load_balancer network_load_balancer endpoints peering".split()})
ICONS.update({n: ("res", "#232F3D") for n in "client users user mobile_client traditional_server servers".split()})
ALIAS = {"opensearch": "elasticsearch_service", "opensearch_service": "elasticsearch_service",
         "msk": "managed_streaming_for_kafka", "alb": "application_load_balancer",
         "nlb": "network_load_balancer", "elb": "elastic_load_balancing", "kms": "key_management_service",
         "ebs": "elastic_block_store", "efs": "elastic_file_system", "cloudwatch": "cloudwatch_2",
         "ses": "simple_email_service", "iam_identity_center": "single_sign_on", "sso": "single_sign_on",
         "acm": "certificate_manager_3", "ssm": "systems_manager", "vpc_peering": "peering",
         "dynamodb_table": "dynamodb", "dynamodb_stream": "dynamodb", "kinesis_data_streams": "kinesis",
         "endpoint": "endpoints", "step_function": "step_functions", "apigateway": "api_gateway"}
# Names that draw an empty or black square in draw.io. The alias above replaces each one.
BROKEN = {"dynamodb_table", "dynamodb_stream", "general_saml_token", "endpoint", "kinesis_data_streams",
          "msk", "vpc_peering", "peering_connection", "iam_identity_center"}

GROUPS = {  # boundary kind -> (grIcon or "", stroke, font, fill, dashed)
    "aws-cloud": ("group_aws_cloud_alt", "#232F3E", "#232F3E", "none", 0),
    "account": ("group_account", "#CD2264", "#CD2264", "none", 0),
    "region": ("group_region", "#00A4A6", "#147EBA", "none", 1),
    "vpc": ("group_vpc2", "#8C4FFF", "#AAB7B8", "none", 0),
    "az": ("", "#147EBA", "#147EBA", "none", 1),
    "public-subnet": ("group_public_subnet", "#7AA116", "#248814", "#F2F6E8", 0),
    "private-subnet": ("group_private_subnet", "#00A4A6", "#147EBA", "#E6F6F7", 0),
    "security-group": ("", "#DD344C", "#DD344C", "none", 0),
    "on-prem": ("group_on_premise", "#5A6C86", "#5A6C86", "none", 0),
}

KIND_STYLE = {
    "compute": "rounded=1;arcSize=12;",
    "client": "rounded=1;arcSize=50;",
    "edge": "shape=process;size=0.04;backgroundOutline=1;",
    "data": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=6;",
    "queue": "shape=step;perimeter=stepPerimeter;fixedSize=1;size=10;",
    "schedule": "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=10;",
    "external": f"rounded=1;arcSize=12;dashed=1;strokeColor={MUTED};fillColor=#F5F5F5;",
}
STATE_STYLE = {
    "building": f"fillColor={SOFT};strokeColor={ACCENT};",
    "planned": f"dashed=1;dashPattern=5 4;strokeColor={MUTED};fontColor={MUTED};",
    "removed": f"strokeColor={RED};fontStyle=8;",
    "unconfirmed": f"dashed=1;dashPattern=1 3;strokeColor={MUTED};fontColor={MUTED};fillColor=#FAFAFA;",
}
EDGE_STYLE = {
    "request": "",
    "data": "strokeWidth=2;endArrow=none;",
    "event": "dashed=1;dashPattern=1 3;strokeWidth=1.6;",
    "deploy": f"dashed=1;dashPattern=6 4;strokeColor={MUTED};",
    "scrape": f"dashed=1;dashPattern=1 4;strokeColor={MUTED};",
}
EDGE_STATE = {
    "building": f"strokeColor={ACCENT};",
    "planned": f"dashed=1;dashPattern=5 4;strokeColor={MUTED};",
    "removed": f"strokeColor={RED};",
    "unconfirmed": f"dashed=1;dashPattern=1 3;strokeColor={MUTED};",
}


def icon_of(name):
    """(pattern, colour, draw.io name) for an icon name, or None when it is not a verified icon."""
    if not name:
        return None
    key = ALIAS.get(str(name), str(name))
    got = ICONS.get(key)
    return (got[0], got[1], key) if got else None


def icon_problem(name):
    """A check message for a part's icon, or None."""
    if icon_of(name):
        return None
    if name in BROKEN:
        return f"icon {name!r} draws an empty box in draw.io"
    return f"icon {name!r} is not a verified draw.io AWS icon, so the .drawio box has no icon"


def cell(root, cid, parent, *, value="", style="", vertex=False, edge=False, source=None, target=None,
         tooltip=None):
    """Append one mxCell (wrapped in a UserObject when it has a tooltip). Returns the mxCell."""
    attrs = {"style": style, "parent": parent}
    if vertex:
        attrs["vertex"] = "1"
    if edge:
        attrs["edge"] = "1"
        if source:
            attrs["source"] = source
        if target:
            attrs["target"] = target
    if tooltip:
        holder = ET.SubElement(root, "UserObject", {"id": cid, "label": value, "tooltip": tooltip})
        return ET.SubElement(holder, "mxCell", attrs)
    return ET.SubElement(root, "mxCell", dict({"id": cid, "value": value}, **attrs))


def geom(c, x, y, w, h):
    ET.SubElement(c, "mxGeometry", {"x": f"{x:g}", "y": f"{y:g}", "width": f"{w:g}", "height": f"{h:g}",
                                    "as": "geometry"})


def polyline(d):
    """The corner points of a diagram.py path."""
    segs = segments(d)
    return [(segs[0][0], segs[0][1])] + [(s[2], s[3]) for s in segs] if segs else []


def along(points, px, py):
    """(t, nearest point) for the point on the polyline closest to (px, py). t runs 0..1."""
    lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(points, points[1:])]
    total = sum(lens) or 1
    best, run = None, 0.0
    for (a, b), ln in zip(zip(points, points[1:]), lens):
        if ln:
            u = max(0.0, min(1.0, ((px - a[0]) * (b[0] - a[0]) + (py - a[1]) * (b[1] - a[1])) / ln ** 2))
        else:
            u = 0.0
        qx, qy = a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])
        dist = (qx - px) ** 2 + (qy - py) ** 2
        if best is None or dist < best[0]:
            best = (dist, (run + u * ln) / total, (qx, qy))
        run += ln
    return best[1], best[2]


def page_xml(m, lay, mode, pre):
    """One <diagram> element: the spec as drawn in one mode (or the only one)."""
    ids = [i for i, _ in modes_of(m)]
    names = dict(modes_of(m))
    shown = [p for p in lay["parts"] if not ids or mode in in_modes(p, ids)]
    sid = {p["id"] for p in shown}
    diagram = ET.Element("diagram", {"id": f"{pre}page", "name": names.get(mode, m.get("title") or "Diagram")})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1400", "dy": "900", "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1", "connect": "1",
        "arrows": "1", "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(int(lay["width"]) + 40),
        "pageHeight": str(int(lay["height"]) + TOP + 40), "math": "0", "shadow": "0"})
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    bg = cell(root, f"{pre}bg", "1", vertex=True,
              style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=none;movable=0;locked=1;")
    geom(bg, 0, 0, lay["width"], lay["height"] + TOP)
    title = (m.get("title") or "Architecture") + (f" · {names[mode]}" if mode in names else "")
    t = cell(root, f"{pre}title", "1", vertex=True, value=f"<b>{escape(title)}</b>",
             style=f"text;html=1;align=left;verticalAlign=middle;fontSize=14;fontColor={FG};")
    geom(t, 20, 6, max(300, lay["width"] - 40), 22)

    # Boundaries: containers, outermost first. Each one's geometry is relative to its parent.
    origin, bcell = {(): (0, 0)}, {(): "1"}
    meta = m.get("boundaries", {}) if isinstance(m.get("boundaries"), dict) else {}
    for n, (path, (x0, y0, x1, y1), blabel) in enumerate(boundary_rects(shown, meta)):
        ox, oy = origin[path[:-1]]
        kind = (meta.get(path[-1]) or {}).get("kind") if isinstance(meta.get(path[-1]), dict) else None
        if kind in GROUPS:
            gr, stroke, font, fill, dashed = GROUPS[kind]
            style = (f"outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=10;fontStyle=1;"
                     f"container=1;pointerEvents=0;collapsible=0;recursiveResize=0;verticalAlign=top;align=left;"
                     f"strokeColor={stroke};fillColor={fill};fontColor={font};dashed={dashed};"
                     + (f"shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.{gr};spacingLeft=30;" if gr else
                        "rounded=0;spacingLeft=8;"))
        else:
            style = ("rounded=1;arcSize=10;absoluteArcSize=1;fillColor=none;strokeColor=#9AA3AE;html=1;"
                     "whiteSpace=wrap;verticalAlign=top;align=left;spacingLeft=8;spacingTop=-3;fontSize=10;"
                     "fontStyle=1;fontColor=#5A6C86;container=1;collapsible=0;recursiveResize=0;")
        bid = f"{pre}b{n}"
        c = cell(root, bid, bcell[path[:-1]], vertex=True, value=escape(str(blabel).upper()), style=style)
        geom(c, x0 - ox, y0 + TOP - oy, x1 - x0, y1 - y0)
        origin[path], bcell[path] = (x0, y0 + TOP), bid

    # Parts, inside their innermost boundary.
    for p in shown:
        path = tuple(p.get("boundary", []))
        ox, oy = origin.get(path, (0, 0))
        label = str(val(p, "label", mode) or p["id"]).upper() + (" ?" if p.get("state") == "unconfirmed" else "")
        sub = val(p, "sub", mode)
        value = f"<b>{escape(label)}</b>" + (f'<br><font style="font-size:10px" color="{MUTED}">{escape(str(sub))}</font>'
                                             if sub else "")
        icon = icon_of(p.get("icon"))
        style = (f"whiteSpace=wrap;html=1;align=left;verticalAlign=middle;spacingLeft={48 if icon else 10};"
                 f"fontSize=11;fontColor={FG};strokeColor={FG};fillColor=#FFFFFF;"
                 + KIND_STYLE.get(p.get("kind"), KIND_STYLE["compute"]) + STATE_STYLE.get(p.get("state"), ""))
        tip = "\n".join(x for x in (val(p, "caption", mode), (f"Source: {val(p, 'source', mode)}"
                                                              if val(p, "source", mode) else "")) if x)
        pid = f"{pre}n-{p['id']}"
        c = cell(root, pid, bcell.get(path, "1"), vertex=True, value=value, style=style, tooltip=tip or None)
        geom(c, p["x"] - ox, p["y"] + TOP - oy, BOX_W, BOX_H)
        if icon:
            pattern, colour, name = icon
            ist = ("sketch=0;outlineConnect=0;dashed=0;html=1;aspect=fixed;" +
                   (f"fillColor={colour};strokeColor=#ffffff;shape=mxgraph.aws4.resourceIcon;"
                    f"resIcon=mxgraph.aws4.{name};" if pattern == "svc" else
                    f"fillColor={colour};strokeColor=none;shape=mxgraph.aws4.{name};"))
            ic = cell(root, f"{pre}i-{p['id']}", pid, vertex=True, style=ist)
            geom(ic, 8, (BOX_H - 32) / 2, 32, 32)

    # Edges, on the canvas, with the routes diagram.py checked as waypoints.
    labels = []
    for n, (e, d, (lx, ly, anchor)) in enumerate(lay["routed"]):
        if e["from"] not in sid or e["to"] not in sid:
            continue
        if ids and not (mode in in_modes(e, ids) and mode in in_modes(lay["byid"][e["from"]], ids)
                        and mode in in_modes(lay["byid"][e["to"]], ids)):
            continue
        pts = polyline(d)
        if len(pts) < 2:
            continue
        a, b = lay["byid"][e["from"]], lay["byid"][e["to"]]
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        clamp = lambda v: max(0.0, min(1.0, v))  # noqa: E731
        style = ("html=1;rounded=0;edgeStyle=none;fontSize=9;fontStyle=1;fontColor=#545B64;"
                 f"labelBackgroundColor=#FFFFFF;strokeColor={FG};endArrow=block;endFill=1;endSize=6;"
                 f"exitX={clamp((sx - a['x']) / BOX_W):.3f};exitY={clamp((sy - a['y']) / BOX_H):.3f};exitPerimeter=0;"
                 f"entryX={clamp((tx - b['x']) / BOX_W):.3f};entryY={clamp((ty - b['y']) / BOX_H):.3f};entryPerimeter=0;"
                 + EDGE_STYLE.get(e.get("kind", "request"), "") + EDGE_STATE.get(e.get("state"), ""))
        text = str(val(e, "label", mode) or "")
        c = cell(root, f"{pre}e{n}", "1", edge=True, source=f"{pre}n-{e['from']}", target=f"{pre}n-{e['to']}",
                 value=escape(text), style=style)
        g = ET.SubElement(c, "mxGeometry", {"relative": "1", "as": "geometry"})
        if len(pts) > 2:
            arr = ET.SubElement(g, "Array", {"as": "points"})
            for x, y in pts[1:-1]:
                ET.SubElement(arr, "mxPoint", {"x": f"{x:g}", "y": f"{y + TOP:g}"})
        if text:
            labels.append((g, pts, text, lx, ly, anchor))
    # Put each label where the page puts it, after the page's collision pass.
    spots = label_spots([("", lx, ly, anchor, text, {None}) for _, _, text, lx, ly, anchor in labels])
    for (g, pts, text, _, _, _), (_, lx, ly, anchor, _) in zip(labels, spots):
        w = len(text) * 5.8 + 4
        cx = lx + w / 2 if anchor == "start" else lx - w / 2 if anchor == "end" else lx
        t, (qx, qy) = along(pts, cx, ly - 3)
        g.set("x", f"{2 * t - 1:.3f}")
        ET.SubElement(g, "mxPoint", {"x": f"{cx - qx:.1f}", "y": f"{ly - 3 - qy:.1f}", "as": "offset"})
    return diagram


def drawio_xml(m):
    """The whole .drawio file as text."""
    lay = placed(m)
    if not lay:
        raise SystemExit("diagram: the spec has no part with an id, a lane, and a row")
    ids = [i for i, _ in modes_of(m)] or [None]
    mx = ET.Element("mxfile", {"host": "draw-infra", "type": "device"})
    for k, mode in enumerate(ids):
        mx.append(page_xml(m, lay, mode, f"m{k}-"))
    ET.indent(mx)
    return ET.tostring(mx, encoding="unicode") + "\n"


def verify(text):
    """Problems in a .drawio file: duplicate ids, missing parents or ends, broken icon names."""
    probs = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return [f"not valid XML: {e}"]
    for d in root.iter("diagram"):
        seen, cells, verts = set(), [], set()
        for el in d.iter():
            if el.tag in ("mxCell", "UserObject") and el.get("id"):
                if el.get("id") in seen:
                    probs.append(f"{d.get('name')}: id {el.get('id')} used twice")
                seen.add(el.get("id"))
        for el in d.iter():
            if el.tag == "UserObject":
                inner = el.find("mxCell")
                cells.append((el.get("id"), inner))
            elif el.tag == "mxCell" and el.get("id"):
                cells.append((el.get("id"), el))
        for cid, c in cells:
            if c.get("vertex") == "1":
                verts.add(cid)
        for cid, c in cells:
            if c.get("parent") and c.get("parent") not in seen:
                probs.append(f"{d.get('name')}: {cid} has a missing parent {c.get('parent')}")
            if c.get("edge") == "1":
                for end in ("source", "target"):
                    if c.get(end) not in verts:
                        probs.append(f"{d.get('name')}: edge {cid} has no {end} box")
            style = c.get("style") or ""
            for key in ("resIcon=mxgraph.aws4.", "shape=mxgraph.aws4."):
                if key in style:
                    name = style.split(key, 1)[1].split(";", 1)[0]
                    if name in BROKEN:
                        probs.append(f"{d.get('name')}: {cid} uses the broken icon {name}")
            if c.get("vertex") == "1":
                g = c.find("mxGeometry")
                if g is None or float(g.get("width", 0)) <= 0 or float(g.get("height", 0)) <= 0:
                    probs.append(f"{d.get('name')}: {cid} has no size")
    return probs


def export_png(src, out, page=1):
    """Export one page of a .drawio to PNG with the draw.io CLI. Returns (ok, message)."""
    exe = shutil.which("drawio") or shutil.which("draw.io")
    if not exe:
        return False, "no draw.io CLI (drawio) on PATH, so no PNG"
    env = dict(os.environ)
    cmd = [exe]
    if not env.get("DISPLAY") and not env.get("WAYLAND_DISPLAY"):
        if os.path.exists("/tmp/.X11-unix/X0"):
            env["DISPLAY"] = ":0"
        elif shutil.which("xvfb-run"):
            cmd = ["xvfb-run", "-a", exe]
        else:
            return False, "draw.io needs a display (none, and no xvfb-run), so no PNG"
    # A snap draw.io sees only its own folder, so stage the files there.
    snap = os.path.realpath(exe).endswith("/snap") or exe.startswith("/snap/")
    work = os.path.expanduser("~/snap/drawio/current/draw-infra") if snap else os.path.dirname(os.path.abspath(out))
    os.makedirs(work, exist_ok=True)
    src_in = os.path.join(work, "in.drawio") if snap else os.path.abspath(src)
    png = os.path.join(work, "out.png") if snap else os.path.abspath(out)
    if snap:
        shutil.copyfile(src, src_in)
    try:
        r = subprocess.run(cmd + ["-x", "-f", "png", "-b", "10", "-p", str(page), "-o", png, src_in],
                           capture_output=True, text=True, timeout=120, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"draw.io export failed: {e}"
    if not os.path.exists(png):
        tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
        return False, f"draw.io export failed: {tail[0]}"
    if snap:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        shutil.move(png, out)
        os.remove(src_in)
    return True, out
