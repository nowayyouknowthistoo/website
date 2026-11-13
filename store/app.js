(function () {
  "use strict";

  // ---- settings: change these to set up the shop ----
  var SHIPPING_US = 8;            // flat rate per order
  var FREE_SHIP_OVER = 150;       // free US shipping at or above this subtotal
  // Paste a checkout link here (Shopify, Stripe Payment Link, Square, etc.).
  // Leave empty and checkout opens an email with the order instead.
  var CHECKOUT_URL = "";
  var ORDER_EMAIL = "orders@example.com";

  var P = window.PRODUCTS || [];
  var app = document.getElementById("app");
  var SIZES = ["XS", "S", "M", "L", "XL", "XXL"];

  // ---- helpers ----
  function $(sel, root) { return (root || document).querySelector(sel); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function money(n) { return "$" + n.toLocaleString("en-US"); }
  function byId(id) { for (var i = 0; i < P.length; i++) if (P[i].id === id) return P[i]; return null; }
  function uniq(arr) { return arr.filter(function (v, i) { return arr.indexOf(v) === i; }); }

  // Drawn tee for items without photos. Text on the chest is the band name.
  function tee(p, back) {
    var name = esc(p.band.toUpperCase());
    var fs = name.length > 14 ? 13 : name.length > 9 ? 16 : 20;
    var art = back
      ? '<text x="100" y="92" text-anchor="middle" font-family="Anton,Impact,sans-serif" font-size="13" fill="' + p.print + '" letter-spacing="1">' + esc(p.title.toUpperCase()).slice(0, 26) + '</text>' +
        [0, 1, 2, 3, 4, 5].map(function (i) { return '<rect x="66" y="' + (104 + i * 11) + '" width="' + (68 - (i % 3) * 8) + '" height="4" fill="' + p.print + '" opacity=".7"/>'; }).join("")
      : '<text x="100" y="86" text-anchor="middle" font-family="Anton,Impact,sans-serif" font-size="' + fs + '" fill="' + p.print + '" letter-spacing=".5">' + name + '</text>' +
        '<circle cx="100" cy="118" r="20" fill="none" stroke="' + p.print + '" stroke-width="3"/>' +
        '<text x="100" y="158" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" fill="' + p.print + '" letter-spacing="2">' + esc(p.year) + '</text>';
    return '<svg viewBox="0 0 200 220" role="img" aria-label="' + esc(p.band + " " + p.title) + '">' +
      '<path d="M70 14 Q100 34 130 14 L176 34 L198 78 L166 92 L158 76 L158 210 L42 210 L42 76 L34 92 L2 78 L24 34 Z" fill="' + p.color + '" stroke="rgba(0,0,0,.18)" stroke-width="1.2"/>' +
      '<path d="M70 14 Q100 ' + (back ? 22 : 34) + ' 130 14" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="3"/>' +
      art + "</svg>";
  }
  function media(p, i) {
    var imgs = p.images || [];
    if (imgs.length) return '<img src="' + esc(imgs[i] || imgs[0]) + '" alt="' + esc(p.band + " " + p.title) + '" loading="lazy">';
    return tee(p, i === 1);
  }
  function views(p) { return (p.images && p.images.length) ? p.images.length : 2; }

  // ---- cart (stored in this browser) ----
  function loadCart() { try { return JSON.parse(localStorage.getItem("sp-cart") || "[]"); } catch (e) { return []; } }
  function saveCart(c) { try { localStorage.setItem("sp-cart", JSON.stringify(c)); } catch (e) {} updateCount(); }
  var cart = loadCart().filter(function (id) { var p = byId(id); return p && !p.sold; });
  function updateCount() { $(".cart-count").textContent = cart.length; }

  function toast(msg) {
    var t = $(".toast");
    if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove("show"); }, 1800);
  }

  function card(p) {
    return '<a class="card' + (p.sold ? " is-sold" : "") + '" href="#/item/' + p.id + '">' +
      '<div class="card-img">' + media(p, 0) +
      (p.sold ? '<span class="badge sold">Sold</span>' : '<span class="badge">' + esc(p.size) + "</span>") +
      "</div>" +
      '<div class="card-meta"><div class="card-band">' + esc(p.band) + "</div>" +
      '<div class="card-title">' + esc(p.title) + " &middot; " + esc(p.year) + "</div>" +
      '<div class="card-row"><span class="price">' + money(p.price) + '</span><span class="mono muted">' + p.pit + '" pit</span></div></div></a>';
  }

  // ---- pages ----
  function home() {
    var feat = P.filter(function (p) { return p.featured && !p.sold; }).slice(0, 4);
    var latest = P.filter(function (p) { return !p.sold; }).slice(0, 8);
    var bands = uniq(P.map(function (p) { return p.band; })).sort();
    var hero = feat[0] || P[0];
    app.innerHTML =
      '<section class="hero"><div>' +
      '<span class="mono muted">Drop 014 &middot; live now</span>' +
      "<h1>Real tour tees. <em>No reprints.</em></h1>" +
      "<p>Original 80s and 90s band shirts, hand-picked and checked for tag, stitch and print. Every one is measured flat, graded honestly, and there's only one of each.</p>" +
      '<div class="btn-row"><a class="btn" href="#/shop">Shop the drop</a><a class="btn ghost" href="#/info">How we grade</a></div>' +
      "</div>" +
      (hero ? '<a class="hero-art" href="#/item/' + hero.id + '">' + media(hero, 0) + '<span class="stamp">Single stitch<br>' + esc(hero.year) + "</span></a>" : "") +
      "</section>" +
      '<div class="trust"><div><b>1 of 1</b><span>Each shirt sells once</span></div><div><b>Authenticated</b><span>Tags, stitch &amp; print checked</span></div><div><b>Measured</b><span>Pit to pit &amp; length on every tee</span></div><div><b>Ships in 2 days</b><span>Tracked, from the US</span></div></div>' +
      '<section class="section"><div class="section-head"><h2>Featured</h2><a href="#/shop">Shop all</a></div><div class="grid">' + feat.map(card).join("") + "</div></section>" +
      '<section class="section"><div class="section-head"><h2>Shop by band</h2></div><div class="band-chips">' +
      bands.map(function (b) { return '<a class="chip" href="#/shop?band=' + encodeURIComponent(b) + '">' + esc(b) + "</a>"; }).join("") +
      "</div></section>" +
      '<section class="section"><div class="section-head"><h2>Just listed</h2><a href="#/shop">View all</a></div><div class="grid">' + latest.map(card).join("") + "</div></section>";
  }

  function shop(q) {
    var state = {
      band: q.band ? q.band.split("|") : [],
      era: q.era ? q.era.split("|") : [],
      genre: q.genre ? q.genre.split("|") : [],
      size: q.size ? q.size.split("|") : [],
      sold: q.sold === "1",
      q: q.q || "",
      sort: q.sort || "new"
    };

    function list(field) { return uniq(P.map(function (p) { return p[field]; })).sort(); }
    function countOf(field, v) { return P.filter(function (p) { return p[field] === v && (state.sold ? p.sold : !p.sold); }).length; }
    function checks(field, title) {
      return "<h4>" + title + "</h4>" + list(field).map(function (v) {
        return '<label><input type="checkbox" data-f="' + field + '" value="' + esc(v) + '"' + (state[field].indexOf(v) > -1 ? " checked" : "") + "> " + esc(v) + '<span class="count">' + countOf(field, v) + "</span></label>";
      }).join("");
    }

    app.innerHTML = '<div class="shop-root">' +
      '<div class="shop-head"><div><span class="mono muted">' + (state.sold ? "Sold archive" : "In stock") + '</span><h1 class="page-title">' + (state.sold ? "Archive" : "Shop all tees") + "</h1></div>" +
      '<div class="toolbar"><button class="btn ghost filter-toggle">Filters</button><select class="sort" aria-label="Sort">' +
      [["new", "Newest"], ["price-asc", "Price, low to high"], ["price-desc", "Price, high to low"], ["year", "Year, oldest first"]].map(function (o) {
        return '<option value="' + o[0] + '"' + (state.sort === o[0] ? " selected" : "") + ">" + o[1] + "</option>";
      }).join("") + "</select></div></div>" +
      '<div class="shop-layout"><aside class="filters">' +
      '<input class="search" type="search" placeholder="Search band, album, year" value="' + esc(state.q) + '" aria-label="Search">' +
      "<h4 style=\"margin-top:22px\">Size</h4><div class=\"size-row\">" + SIZES.map(function (s) {
        return '<button class="chip' + (state.size.indexOf(s) > -1 ? " on" : "") + '" data-size="' + s + '">' + s + "</button>";
      }).join("") + "</div>" +
      checks("era", "Era") + checks("genre", "Genre") + checks("band", "Band") +
      '<h4>Show</h4><label><input type="checkbox" class="sold-toggle"' + (state.sold ? " checked" : "") + "> Sold archive only</label>" +
      '</aside><div><div class="grid results"></div></div></div></div>';

    function render() {
      var term = state.q.trim().toLowerCase();
      var items = P.filter(function (p) {
        if (state.sold ? !p.sold : p.sold) return false;
        if (state.band.length && state.band.indexOf(p.band) < 0) return false;
        if (state.era.length && state.era.indexOf(p.era) < 0) return false;
        if (state.genre.length && state.genre.indexOf(p.genre) < 0) return false;
        if (state.size.length && state.size.indexOf(p.size) < 0) return false;
        if (term && (p.band + " " + p.title + " " + p.year + " " + p.tag).toLowerCase().indexOf(term) < 0) return false;
        return true;
      });
      if (state.sort === "price-asc") items.sort(function (a, b) { return a.price - b.price; });
      if (state.sort === "price-desc") items.sort(function (a, b) { return b.price - a.price; });
      if (state.sort === "year") items.sort(function (a, b) { return a.year.localeCompare(b.year); });
      $(".results").innerHTML = items.length ? items.map(card).join("") : '<div class="empty" style="grid-column:1/-1">Nothing matches those filters yet. New tees drop weekly.</div>';
      var qs = [];
      ["band", "era", "genre", "size"].forEach(function (k) { if (state[k].length) qs.push(k + "=" + encodeURIComponent(state[k].join("|"))); });
      if (state.sold) qs.push("sold=1");
      if (state.q) qs.push("q=" + encodeURIComponent(state.q));
      if (state.sort !== "new") qs.push("sort=" + state.sort);
      history.replaceState(null, "", "#/shop" + (qs.length ? "?" + qs.join("&") : ""));
    }

    $(".shop-root").addEventListener("change", function (e) {
      var t = e.target;
      if (t.dataset.f) {
        var arr = state[t.dataset.f], i = arr.indexOf(t.value);
        if (t.checked && i < 0) arr.push(t.value); else if (!t.checked && i > -1) arr.splice(i, 1);
      } else if (t.classList.contains("sold-toggle")) { state.sold = t.checked; }
      else if (t.classList.contains("sort")) { state.sort = t.value; }
      render();
    });
    $(".search").addEventListener("input", function (e) { state.q = e.target.value; render(); });
    Array.prototype.forEach.call(app.querySelectorAll("[data-size]"), function (b) {
      b.addEventListener("click", function () {
        var s = b.dataset.size, i = state.size.indexOf(s);
        if (i > -1) state.size.splice(i, 1); else state.size.push(s);
        b.classList.toggle("on"); render();
      });
    });
    $(".filter-toggle").addEventListener("click", function () { $(".filters").classList.toggle("open"); });
    render();
  }

  function item(id) {
    var p = byId(id);
    if (!p) { app.innerHTML = '<div class="empty"><h1 class="page-title">Not found</h1><p>That tee may have been removed.</p><a class="btn" href="#/shop">Back to shop</a></div>'; return; }
    var inCart = cart.indexOf(p.id) > -1;
    var n = views(p), thumbs = "";
    for (var i = 0; i < n; i++) thumbs += '<button class="' + (i === 0 ? "on" : "") + '" data-i="' + i + '" aria-label="View ' + (i + 1) + '">' + media(p, i) + "</button>";
    var related = P.filter(function (o) { return o.id !== p.id && !o.sold && (o.genre === p.genre || o.era === p.era); }).slice(0, 4);

    app.innerHTML =
      '<div class="crumbs"><a href="#/">Home</a> / <a href="#/shop">Shop</a> / <a href="#/shop?band=' + encodeURIComponent(p.band) + '">' + esc(p.band) + "</a></div>" +
      '<div class="product"><div><div class="gallery-main">' + media(p, 0) + '</div><div class="thumbs">' + thumbs + "</div></div>" +
      '<div class="p-info"><span class="mono muted">' + esc(p.year) + " &middot; " + esc(p.genre) + "</span>" +
      "<h1>" + esc(p.band) + '</h1><p class="sub">' + esc(p.title) + "</p>" +
      '<div class="p-price">' + money(p.price) + '<span class="size-box">Size ' + esc(p.size) + "</span></div>" +
      '<div class="measure"><svg viewBox="0 0 200 220"><path d="M70 14 Q100 34 130 14 L176 34 L198 78 L166 92 L158 76 L158 210 L42 210 L42 76 L34 92 L2 78 L24 34 Z" fill="none" stroke="currentColor" stroke-width="5"/><path d="M48 84 H152" stroke="var(--accent)" stroke-width="6" stroke-dasharray="10 6"/><path d="M100 30 V204" stroke="var(--accent)" stroke-width="6" stroke-dasharray="10 6"/></svg>' +
      '<div><div class="num">' + p.pit + '"</div><div class="lbl">Pit to pit</div></div><div><div class="num">' + p.length + '"</div><div class="lbl">Length</div></div></div>' +
      (p.sold
        ? '<button class="btn" disabled>Sold</button>'
        : '<button class="btn add">' + (inCart ? "In your bag &rarr; view bag" : "Add to bag") + "</button>") +
      '<dl class="specs">' +
      [["Tag", p.tag], ["Stitching", p.stitch], ["Made in", p.madeIn], ["Condition", p.condition], ["Tagged size", p.size]].map(function (r) {
        return "<div><dt>" + r[0] + "</dt><dd>" + esc(r[1]) + "</dd></div>";
      }).join("") + "</dl>" +
      '<p class="note"><b>Condition notes:</b> ' + esc(p.notes) + "</p>" +
      '<p class="note">Measured laid flat. Vintage sizing runs small, so go by the measurements, not the tag. See the <a href="#/info" style="text-decoration:underline">sizing guide</a>.</p>' +
      "</div></div>" +
      (related.length ? '<section class="section"><div class="section-head"><h2>You might dig</h2></div><div class="grid">' + related.map(card).join("") + "</div></section>" : "");

    Array.prototype.forEach.call(app.querySelectorAll(".thumbs button"), function (b) {
      b.addEventListener("click", function () {
        $(".gallery-main").innerHTML = media(p, +b.dataset.i);
        Array.prototype.forEach.call(app.querySelectorAll(".thumbs button"), function (x) { x.classList.toggle("on", x === b); });
      });
    });
    var add = $(".add");
    if (add) add.addEventListener("click", function () {
      if (cart.indexOf(p.id) > -1) { location.hash = "#/cart"; return; }
      cart.push(p.id); saveCart(cart);
      add.innerHTML = "In your bag &rarr; view bag";
      toast(p.band + " added to bag");
    });
  }

  function cartPage() {
    var items = cart.map(byId).filter(Boolean);
    if (!items.length) {
      app.innerHTML = '<div class="cart"><h1 class="page-title">Your bag</h1><div class="empty">Your bag is empty.<br><br><a class="btn" href="#/shop">Shop tees</a></div></div>';
      return;
    }
    var sub = items.reduce(function (s, p) { return s + p.price; }, 0);
    var ship = sub >= FREE_SHIP_OVER ? 0 : SHIPPING_US;
    app.innerHTML = '<div class="cart"><h1 class="page-title">Your bag</h1><p class="muted">Items aren\'t reserved until checkout. Every tee is one of one.</p>' +
      items.map(function (p) {
        return '<div class="cart-item"><a class="thumb" href="#/item/' + p.id + '">' + media(p, 0) + "</a>" +
          '<div><div class="card-band">' + esc(p.band) + '</div><div class="muted">' + esc(p.title) + " &middot; " + esc(p.size) + " &middot; " + p.pit + '" pit</div>' +
          '<button class="link-btn" data-rm="' + p.id + '">Remove</button></div><div class="price">' + money(p.price) + "</div></div>";
      }).join("") +
      '<div class="totals"><div><span>Subtotal</span><span>' + money(sub) + "</span></div>" +
      "<div><span>US shipping</span><span>" + (ship ? money(ship) : "Free") + "</span></div>" +
      '<div class="grand"><span>Total</span><span>' + money(sub + ship) + "</span></div>" +
      '<button class="btn checkout">Checkout</button></div></div>';

    Array.prototype.forEach.call(app.querySelectorAll("[data-rm]"), function (b) {
      b.addEventListener("click", function () { cart.splice(cart.indexOf(b.dataset.rm), 1); saveCart(cart); cartPage(); });
    });
    $(".checkout").addEventListener("click", function () {
      if (CHECKOUT_URL) { location.href = CHECKOUT_URL; return; }
      var body = "Hi! I'd like to buy:\n\n" + items.map(function (p) { return "- " + p.band + " " + p.title + " (" + p.size + ") " + money(p.price) + " [" + p.id + "]"; }).join("\n") +
        "\n\nTotal with shipping: " + money(sub + ship) + "\n\nShip to:\n";
      location.href = "mailto:" + ORDER_EMAIL + "?subject=" + encodeURIComponent("Order request") + "&body=" + encodeURIComponent(body);
    });
  }

  function info() {
    app.innerHTML = '<div class="info"><span class="mono muted">Help</span><h1 class="page-title">Info</h1>' +
      "<h2>Sizing guide</h2><p>Every tee is measured laid flat. <b>Pit to pit</b> is straight across the chest, one inch below the armpits. <b>Length</b> runs from the top of the collar to the hem. Lay a tee you already love flat, measure it, and compare.</p>" +
      "<table><tr><th>Typical modern size</th><th>Pit to pit</th><th>Length</th></tr>" +
      "<tr><td>S</td><td>18&ndash;19\"</td><td>26&ndash;27\"</td></tr><tr><td>M</td><td>20&ndash;21\"</td><td>27&ndash;28\"</td></tr><tr><td>L</td><td>21.5&ndash;22.5\"</td><td>28&ndash;29\"</td></tr><tr><td>XL</td><td>23&ndash;24\"</td><td>29&ndash;30\"</td></tr></table>" +
      "<h2>Condition grading</h2><table><tr><th>Grade</th><th>What it means</th></tr>" +
      "<tr><td>9&ndash;10</td><td>Like new or barely worn. No flaws worth noting.</td></tr>" +
      "<tr><td>7&ndash;8</td><td>Worn and loved. Light fading, print cracking, or a tiny pinhole. All flaws listed.</td></tr>" +
      "<tr><td>5&ndash;6</td><td>Heavily worn. Holes, stains or strong fading. Priced for it.</td></tr></table>" +
      "<h2>How we check a tee</h2><p>We look at the tag, the stitching on the sleeves and hem, the print and any copyright date. A single-stitch hem, a period tag (Brockum, Giant, Winterland, Screen Stars) and a dated print are the usual signs. We don't list reprints or bootlegs unless they're old and described that way.</p>" +
      "<h2>Shipping</h2><p>Orders ship within 2 business days with tracking. US shipping is " + money(SHIPPING_US) + ", free over " + money(FREE_SHIP_OVER) + ". International shipping is calculated at checkout.</p>" +
      "<h2>Returns</h2><p>Every item is one of one and described as accurately as we can, so all sales are final. If something arrives not as described, email us within 3 days of delivery and we'll make it right.</p>" +
      '<h2>Contact</h2><p>Questions, more photos, or something you\'re hunting for? Email <a style="text-decoration:underline" href="mailto:' + ORDER_EMAIL + '">' + ORDER_EMAIL + "</a>.</p></div>";
  }

  // ---- router ----
  function route() {
    var h = location.hash.replace(/^#/, "") || "/";
    var parts = h.split("?"), path = parts[0], q = {};
    (parts[1] || "").split("&").forEach(function (kv) { if (!kv) return; var s = kv.split("="); q[s[0]] = decodeURIComponent(s[1] || ""); });
    $(".main-nav").classList.remove("open");
    Array.prototype.forEach.call(document.querySelectorAll(".main-nav a"), function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + h); });
    if (path.indexOf("/item/") === 0) item(path.slice(6));
    else if (path === "/shop") shop(q);
    else if (path === "/cart") cartPage();
    else if (path === "/info") info();
    else home();
    window.scrollTo(0, 0);
  }

  $(".menu-btn").addEventListener("click", function () {
    var nav = $(".main-nav"); nav.classList.toggle("open");
    this.setAttribute("aria-expanded", nav.classList.contains("open"));
  });
  document.getElementById("yr").textContent = new Date().getFullYear();
  window.addEventListener("hashchange", route);
  updateCount();
  route();
})();
