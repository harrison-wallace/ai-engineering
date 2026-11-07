// Paste as the `function` argument of the Playwright browser_evaluate tool
// (or run in DevTools). Read-only: it inspects computed styles and returns counts
// plus up to 3 example selectors per signal. Field names match tells.md.
() => {
  const all = [...document.querySelectorAll('body *')].filter(
    (el) => el.offsetParent !== null || getComputedStyle(el).position === 'fixed'
  );
  const vh = innerHeight;
  const out = {};
  const ex = {};
  const sel = (el) =>
    el.tagName.toLowerCase() +
    (el.id ? '#' + el.id : '') +
    (typeof el.className === 'string' && el.className
      ? '.' + el.className.trim().split(/\s+/).slice(0, 4).join('.')
      : '');
  const hit = (k, el) => {
    out[k] = (out[k] || 0) + 1;
    (ex[k] ||= []).length < 3 && ex[k].push(sel(el));
  };
  const lum = (c) => {
    const m = c.match(/[\d.]+/g);
    if (!m) return null;
    const [r, g, b] = m.slice(0, 3).map((v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const bgOf = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const c = getComputedStyle(e).backgroundColor;
      if (c && !/rgba\(.*,\s*0\)$/.test(c) && c !== 'transparent') return c;
    }
    return 'rgb(255,255,255)';
  };
  const fonts = new Set();
  const radii = {};
  const isBox = (s) =>
    parseFloat(s.borderRadius) >= 8 &&
    (parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none');

  for (const el of all) {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const bi = s.backgroundImage;
    fonts.add(s.fontFamily.split(',')[0].replace(/["']/g, '').trim());

    if (/linear-gradient|conic-gradient/.test(bi)) hit('gradients', el);
    if (/radial-gradient/.test(bi)) hit('radialGradients', el);
    if ((s.backgroundClip === 'text' || s.webkitBackgroundClip === 'text') && bi !== 'none')
      hit('gradientText', el);
    if (/blur/.test(s.backdropFilter || s.webkitBackdropFilter || '')) hit('backdropBlur', el);
    if (/(rgba?\([^)]*\)\s+)?0px 0px (2\d|[3-9]\d|\d{3})px/.test(s.boxShadow)) hit('glowShadows', el);

    if (s.textTransform === 'uppercase' && parseFloat(s.letterSpacing) > 0.5 && parseFloat(s.fontSize) <= 14 && el.innerText?.trim())
      hit('eyebrows', el);
    if (/^H[1-3]$/.test(el.tagName)) {
      hit('headings', el);
      if ([...el.querySelectorAll('span,em,i')].some((c) => {
        const cs = getComputedStyle(c);
        return cs.fontStyle === 'italic' || cs.fontFamily !== s.fontFamily || cs.color !== s.color || cs.backgroundClip === 'text';
      })) hit('headingAccents', el);
      if (/\p{Extended_Pictographic}/u.test(el.textContent)) hit('emojiHeadings', el);
    }

    const bl = parseFloat(s.borderLeftWidth), bt = parseFloat(s.borderTopWidth);
    if (bl >= 2 && bl > bt && parseFloat(s.borderRadius) > 0) hit('leftStripes', el);

    if (isBox(s) && r.width > 120) {
      hit('boxes', el);
      radii[s.borderRadius] = (radii[s.borderRadius] || 0) + 1;
      for (let p = el.parentElement; p && p !== document.body; p = p.parentElement)
        if (isBox(getComputedStyle(p))) { hit('nestedBoxes', el); break; }
    }

    if (r.width <= 56 && r.width >= 28 && Math.abs(r.width - r.height) < 4 && parseFloat(s.borderRadius) >= 6 && el.querySelector('svg') && s.backgroundColor !== 'rgba(0, 0, 0, 0)')
      hit('iconChips', el);

    if (r.top > vh && (s.opacity === '0' || (s.transform !== 'none' && s.transitionProperty !== 'none')))
      hit('scrollReveal', el);
    if (s.animationIterationCount === 'infinite' && !/spin/i.test(s.animationName)) hit('infiniteAnims', el);

    // Fake window chrome: a parent whose 3 children are all 8–16px dots
    const dot = (c) => {
      const b = c.getBoundingClientRect();
      return b.width >= 8 && b.width <= 16 && Math.abs(b.width - b.height) < 2 &&
        (getComputedStyle(c).borderRadius === '50%' || parseFloat(getComputedStyle(c).borderRadius) >= b.width / 2);
    };
    if (el.children.length === 3 && [...el.children].every(dot)) hit('trafficLights', el);

    if (el.childNodes.length && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 20)) {
      const L1 = lum(s.color), L2 = lum(bgOf(el));
      if (L1 != null && L2 != null) {
        const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
        if (cr < 4.5) hit('lowContrast', el);
      }
    }

    if (r.top < vh && r.height < 40 && r.width < 360 && parseFloat(s.borderRadius) >= r.height / 2 - 1 && el.innerText?.trim() && el.innerText.length < 60) {
      const h1 = document.querySelector('h1');
      if (h1 && r.bottom <= h1.getBoundingClientRect().top + 4) out.heroPill = el.innerText.trim();
    }
  }

  // Rows of 3–4 same-shaped sibling boxes
  const rows = new Set();
  for (const el of all) {
    const kids = [...el.children].filter((c) => isBox(getComputedStyle(c)));
    if (kids.length >= 3 && kids.length <= 4 && kids.length === el.children.length) {
      const sig = (c) => [...c.children].map((x) => x.tagName).join(',');
      const tops = kids.map((k) => Math.round(k.getBoundingClientRect().top));
      if (new Set(kids.map(sig)).size === 1 && new Set(tops).size === 1) rows.add(sel(el));
    }
  }

  const text = document.body.innerText;
  return {
    ...out,
    fonts: [...fonts],
    radii,
    cardRows: [...rows].slice(0, 5),
    words: text.split(/\s+/).filter(Boolean).length,
    emDashes: (text.match(/—/g) || []).length,
    examples: ex,
  };
};
