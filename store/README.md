# Shop website

A storefront for vintage band tees. It's plain HTML, CSS and JavaScript with no build step, so it can be hosted for free on GitHub Pages, Netlify or Cloudflare Pages.

To preview it locally, run `python3 -m http.server` in this folder and open http://localhost:8000.

## Pages
- **Home:** hero, featured tees, shop by band, just listed
- **Shop:** filter by size, era, genre and band, plus search and sort. There's also a sold archive.
- **Item:** photos, price, size, pit-to-pit and length, tag, stitching, made in, condition grade and notes
- **Bag:** one of each item, with flat-rate shipping that's free over a set amount
- **Info:** sizing guide, condition grading, how tees are checked, shipping, returns and contact

## Adding inventory
Edit `products.js`, which has one entry per shirt. Put photos in `images/` and list them in `images: [...]`. When a shirt sells, set `sold: true` and it moves to the archive.

## Settings
At the top of `app.js` you can set the shipping rate, the free-shipping threshold, `CHECKOUT_URL` (for example a Shopify or Stripe Payment Link) and `ORDER_EMAIL`. If there's no checkout link, the Checkout button opens an email with the order in it.

The shop name ("Second Pressing") is a placeholder in `index.html`.
