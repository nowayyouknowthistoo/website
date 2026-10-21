"""Build output/leftover_stock_stores.html: shops that still hold pre-2010 unsold licensed stock."""
import html, pathlib

# (section, name, url, kind, since, strength, how, evidence, dig)
# strength: a = strong, b = worth a look, c = ask them / small. how: direct, proxy, wholesale, ask
# kind: tags shown on the row. Evidence marked "(search index)" was read from search snippets because the site blocked the fetcher.
S = [
# ---------- warehouse & deadstock ----------
("dead","Graphitti Designs","https://www.graphittidesigns.com/shop/sitemap.php","Comics · Marvel/DC/indie","1982","a","direct",
 "Its own shop sitemap lists <b>1,661 apparel items</b>, and 527 of them are marked \"L/A\". Old designs still listed include: six <q>Kingdom Come</q> tees by Alex Ross (1996), <q>JLA: Identity Crisis</q> (2004), <q>Infinite Crisis</q> by Jim Lee (2005), <q>52</q> (2006), <q>Batman R.I.P.</q> (2008), <q>Blackest Night</q> (2009), 16 Sin City tees (a 2005 license), <q>300 Logo II</q> by Frank Miller, Sandman <q>Death</q> tees, plus Cerebus, Bone, Madman, Grendel, Groo, Strangers in Paradise and <q>Obama: Time for a Change</q> (2008).",
 "Go through the sitemap and open every L/A item. Then email them about the remaining sizes and a bulk buy. This is the deepest source on the list."),
("dead","Opa's Vintage Gal","https://opasvintagegal.com/","Pop culture · promo tees","1952 (wholesaler)","b","direct",
 "The stock comes from a West Texas wholesaler founded in 1952: <q>Genuine New Old Stock… untouched inventory… never sold… hidden… for over 30 years</q>. A site search for t-shirt returns 62 results, including <b>1980s Atari dealer promo tees</b> (Pac-Man, Defender, Berzerk, Yars' Revenge) in several sizes at $65–75.",
 "Search for t-shirt. Use their \"Request Line\" to ask what else is boxed up. Most of the stock is electronics; apparel is a small part of it."),
("dead","Starbase Atlanta","https://starbaseatlanta.com/product-category/star-trek/","Sci-fi · TV · cartoons","1976","a","direct",
 "A convention dealer since 1976 that has done 1,500+ shows. It still sells unsold show stock marked <q>NEW UNWORN</q>. That includes Star Trek DS9 <q>Seventh Season Crew</q> (1998–99), Enterprise and TNG tees, Stargate SG-1 (<q>1st Season Cast</q>, <q>Homeworld Security</q>) and Atlantis. The Star Trek category has 816 items, Stargate 70, Animation 608, and \"Movie/TV Sci-Fi, Horror, Fantasy Other\" 895.",
 "Sort the Star Trek, Stargate, Animation and \"Movie / TV Sci-Fi, Horror Fantasy Other\" categories by price. Also check their eBay store, which the site says holds <q>rare and unique items not listed on this site</q>."),
("dead","ToyWiz","https://toywiz.com/halo-3-they-do-their-part-t-shirt-adult-xl/","Video games · anime · wrestling","store mid-1980s","a","direct",
 "Each product page shows the maker and a <q>Release Date</q>, which makes old stock easy to spot. In stock: <q>Halo 3 They Do Their Part</q> (Changes, <q>Release Date: April 2009</q>) in L and XL, <q>Halo 3 Faded Metal Helmet</q>, a Mario Kart Wii tee (2008), and Domo tees by Changes and Ripple Junction. There is also a 2006 Naruto tee and 2006-era WWE youth tees.",
 "Their T-shirt category loads badly, so Google <code>site:toywiz.com \"T-Shirt [Adult\"</code> and <code>site:toywiz.com \"Changes\"</code>, then check the Release Date on each page."),
("dead","Iron On Station","https://www.irononstation.com/pages/about-us","Iron-on transfers · 60s–80s","online 1997","b","direct",
 "Sells 667 unused original transfer sheets printed 1966–1984, under licenses from Disney, Warner Bros, Hanna-Barbera, Star Wars 1977, Battlestar Galactica and Mork &amp; Mindy. Their statement: <q>Original old stock only. No reproductions.</q>",
 "Not finished tees. Useful only if you'd press real period graphics onto old blanks yourself."),
("dead","Dharma Rose (cool-shirts.com)","https://cool-shirts.com/","Tee shop","2001","b","ask",
 "The homepage says <q>since we opened in 2001</q> and that it is <q>time to close shop</q>. A store that is closing down sells off everything, back stock included.",
 "Email them about buying the remaining stock in one lot before it's gone."),

# ---------- comics & pop culture back-stock ----------
("pop","Westfield Comics","https://westfieldcomics.com","Comics · Marvel","40+ yrs","b","direct",
 "(search index) The backlist still shows <q>Spider-Man: Eye of the Spider… T-Shirt… Release Date: 08-29-2007</q>, <q>Marvel Zombies: Corroded Spidey… 06-27-2007</q>, <q>Marvel Zombies: Green Goblin… 07-25-2007</q> and a Graphitti <q>Golden Age Green Lantern Symbol</q> tee.",
 "Go to Stock Backlist Sale Items, then Apparel. The site blocked my fetcher, so check stock in your own browser."),
("pop","Noble Knight Games","https://www.nobleknight.com/subcategory/apparel","Comics · games","1997","b","direct",
 "(search index) The apparel section has a <q>Graphitti Designs</q> brand count of 96, plus product lines <q>Sin City T-Shirts (Graphitti Designs)</q>, Green Lantern, Batman and <q>Assorted T-Shirts (Marvel)</q>. Many are marked <q>Out of Print</q> or <q>Last Stocked</q>.",
 "Filter apparel to in-stock, then go through the Graphitti and Marvel lines. Most may already be sold out."),
("pop","Alternate Worlds","https://alternateworlds.com.au/product-category/clothing-etc/comic-related-t-shirts/","Comics · movies (Australia)","\"Australia's oldest comic store\"","b","direct",
 "(search index) It lists 26 comic tees, including a <q>GRAPHITTI 1993</q> tee, a <q>CROW T-SHIRT: FLESH &amp; BLOOD</q> (1993) and <q>CITY OF LOST CHILDREN T-S 1998</q>.",
 "A small section, but genuine 90s licensed stock. They ship from Melbourne."),
("pop","Jay &amp; Silent Bob's Secret Stash","https://jayandsilentbob.com/collections/vintage-askew","Movies · View Askew","1997 (store)","b","direct",
 "Has a <q>Vintage Askew</q> collection of about 10 tees, including <q>Legends of the Dork Knights</q> from Mallrats, Clerks II (2006), <q>Zack and Miri</q> (2008) and Bluntman &amp; Chronic.",
 "Ask whether these are original old stock. They're priced like new ($30–40)."),
("pop","TV Store Online","https://www.tvstoreonline.com/","Movies · TV · bands","2000s","b","direct",
 "Still has catalog sections for Napoleon Dynamite, Old School, The Hangover and Scott Pilgrim, which are licenses most shops dropped years ago.",
 "Mostly later reprints. Check tags on anything from the 2000s movie sections."),
("pop","SuperHeroStuff","https://www.superherostuff.com","Superhero · games","1999","c","direct",
 "Says <q>offering officially licensed merchandise to fans since 1999</q>. Product pages from around 2008 are still up (Halo 3 Master Chief Tattoo tee), but the ones I checked were sold out.",
 "Search 2007–09 titles (Dark Knight, Iron Man 2008, Halo 3) and watch for leftover sizes."),
("pop","Robert's Anime Corner Store","https://www.animecornerstore.com/animeapparrel.html","Anime","online 1997","c","ask",
 "Has been <q>online since 1997</q> and has a warehouse in Winchester, VA. Only about 14 apparel items are listed (InuYasha, Shi).",
 "Email them about warehouse back-stock. Not much is listed online."),
("pop","Mandarake","https://order.mandarake.co.jp","Anime · Ghibli (Japan)","1980","b","direct",
 "The Nakano store buys mostly <q>未使用</q> (unused) tees and says <q>劇場公開時アパレル</q> (theatrical-release-era apparel) is especially welcome. They ship worldwide and the site has English pages.",
 "Search <q>Tシャツ 未使用</q> or <q>当時物 Tシャツ</q> plus a title (ナウシカ = Nausicaä, エヴァ = Evangelion, トトロ = Totoro)."),
("pop","Ringside Collectibles","https://www.ringsidecollectibles.com/JakksFigures/owent.html","Wrestling","1999","c","ask",
 "A page from 1999 is still live, selling an <q>officially licensed WWF</q> Owen Hart <q>King of Harts</q> tee in L and XL at $29.99. The cart is an ancient Miva script.",
 "Email them about any Attitude-era WWF shirts still in storage."),

# ---------- warehouses to call ----------
("call","Intergalactic Trading Co.","https://intergalactic-patches.com","Sci-fi · Star Trek","1975","a","ask",
 "About page: <q>25,000 square feet of space filled with a 40-year accumulation of sci-fi collectibles</q>. Homepage: <q>rare, out of production items</q>. They have done 1,000+ conventions. A vintage Star Trek DS9 sweatshirt is listed.",
 "Very little apparel is listed online, so call or email about warehouse tee stock. They also run two eBay stores and booths in Orlando antique malls."),
("call","MTC Toys","https://mtctoys.com/t-shirts/","Movies · TV · horror","~35 yrs","b","ask",
 "Known at Comic-Cons as <q>the t-shirt shop</q>: <q>over 1200 t-shirt styles</q> and <q>over 600 clearance tees at prices 40–50% off</q>. Their eBay listings say <q>new old stock from our warehouse, at least 10 years old</q>, but on mouse pads, not tees.",
 "Ask about the 600 clearance tees and any boxed warehouse tee stock. The tees on the website are current reprints."),
("call","OnHollywood / Star500","https://www.onhollywood.com/store/home.php?cat=3766","Bands · movies (wholesale)","1996","b","wholesale",
 "Footer reads <q>Copyright © 1996</q>, and the site claims <q>Established 1996 ● 4,000+ items in stock</q>. The clearance page lists Hellraiser, Boondock Saints, Cheech &amp; Chong, Sebastian Bach and Wanted (2008), and the catalog includes Manson <q>Mechanical Animals</q>.",
 "Open a wholesale account, then go through Clearance and Movie &amp; TV Tees. Print years aren't shown."),
("call","Bulk Vintage Clothing","https://www.bulkvintage.com/category/deadstock-unworn-vintage.html","Wholesale bundles","2009","b","wholesale",
 "Has a <q>Deadstock NOS Unworn Vintage</q> category, including <q>Deadstock (never worn) Mens 1980s/90s shortsleeve shirts, by the bundle</q>. Their offer: <q>If there is a product you need, but do not see listed, please email us.</q>",
 "Email them asking for deadstock graphic tees and crewnecks specifically."),
("call","Rockaway Records","https://rockaway.com/collections/clothing","Bands · LA","decades","c","direct",
 "21 clothing items, all period originals: Soundgarden <q>1994 Promo Shirt Designed by Pushead</q>, Pink Floyd 1994 Division Bell, Megadeth 1992, Def Leppard 1988. Some were owned by the artists.",
 "Ask whether they hold more shirts offline. Prices are high ($150–250)."),

# ---------- music ----------
("music","Woodstock Trading Co.","https://www.woodstocktradeco.com/","Classic rock · Dead (NJ)","1988","b","ask",
 "The homepage is listing <q>Vintage (1999) Mushroom Peace Tie Dye Shirt</q>, a <q>Vintage 1996 Rusted Root Concert Poster</q> and a <q>Nine Inch Nails Woodstock 94 Dog Tag</q>, all pulled from their own back room.",
 "Email them for unlisted 90s tees."),
("music","Band T-Shirts Australia","https://www.bandtshirts.com.au/","Bands · ex-tour (Australia)","2000s","b","direct",
 "Sells <q>Official Licensed and Ex-tour T-Shirts</q> and has a <q>From The Archive</q> section covering 441 bands.",
 "Check From The Archive first, then Sale."),
("music","Wolfgang's","https://www.wolfgangs.com/","Concert memorabilia","2003","b","direct",
 "Built on promoter Bill Graham's archive, and it sells <q>Concert T-Shirts</q> alongside vintage posters.",
 "Look in the vintage clothing section. Prices are collector level."),
("music","RevHQ","https://revhq.com/collections/trustkill","Hardcore · metalcore","1987","c","direct",
 "Slogan: <q>Hardcore Since 1987</q>. It still hosts storefronts for 2000s labels Trustkill, Equal Vision, Indecision and Facedown. I saw only records there, no pre-2010 tees confirmed.",
 "Check the Shirts collection filtered to those labels, plus Markdowns and Damaged/Discounted."),
("japan","DEAD STOCK TOKYO (in What'z up)","https://whatzup.thebase.in","Movies · cartoons · bands","unconfirmed","a","proxy",
 "(search index) Their statement: <q>DEAD STOCK ONLY</q>, selling <q>Vintage (主に60年代から2000年代初頭) の DEAD STOCK (売れ残り)</q> (unsold leftovers from the 60s to early 2000s). Listings include <q>1999 The Mummy 'ILM Visual Effects Crew' T-shirt</q> in L and XL, <q>1991 The Doors 'The Movie' L/S</q>, 90s Star Wars, 90s Simpsons, <q>2004 Family Guy</q>, 1999 Sega Dreamcast, Naruto and early-90s Mountain Dew.",
 "Search the store for 【DST】 or \"Dead Stock\". New stock arrives at weekends. For mail orders, DM @dead_stock_tokyo. This is the closest match on the list for movie and cartoon tees."),
("japan","Green Heaven","https://greenheaven.ocnk.net/product-list?keyword=デッドストック","Bands · movies","unconfirmed","a","proxy",
 "Has a long deadstock archive: <q>デッドストック 90's They Might Be Giants ツアー</q>, Green Day Dookie, a Pink Floyd 1994 tour tee, Cannibal Corpse 1992, Sublime 1998, Sick of It All 1995, White Zombie <q>Super Pig</q>, Beastie Boys <q>Check Your Head</q>, and an original 80s <q>The Thing</q> movie tee. In stock now: Electric Boys 80s and an 80s Budman tee.",
 "Search デッドストック and look through the SOLD OUT archive to see what they keep finding. Contact them with your wants."),
("japan","BerBerJin","https://webstore.berberjin.com/view/category/deadstock","Vintage · Harajuku","1998","b","ask",
 "(search index) The deadstock category had 18 items, e.g. <q>90's STADIUM COURT 'MR.PEANUT'</q>. They <b>cancel orders sent to forwarding services</b>.",
 "You'd need someone in Japan to buy for you."),
("japan","Wroote","https://wrootevtg.base.ec","Movies · sweats","unconfirmed","b","proxy",
 "(search index) Listings include <q>Dead stock!! 90s Titanic Movie t shirt [XL]</q> (two units), a deadstock 90s Sears tee, and a USA-made 90s Russell sweatshirt with its <q>$16.99</q> tag still on.",
 "Search for \"Dead stock\"."),
("japan","Cozy Vintage","https://cozyvintage.stores.jp","Snapbacks","unconfirmed","b","proxy",
 "Lists many <b>DEADSTOCK 80s–90s snapbacks</b> at ¥3,520–4,950, e.g. <q>'Car 54, Where Are You?'</q> embroidered, <q>OPERATION DESERT STORM</q> and DuPont Stren. They also <q>卸売りをしています</q> (sell wholesale) to dealers via info@used-cozy.com.",
 "Ask for a wholesale lot of deadstock snapbacks."),
("japan","Flamingo Online","https://flamingo-online.jp","Harley-Davidson","unconfirmed","c","proxy",
 "(search index) A <q>HARLEY-DAVIDSON Tシャツ大量入荷</q> (large intake of Harley tees) page describes them as <q>未使用のデッドストック</q> (unused deadstock). The era isn't stated.",
 "Worth a manual check if you sell Harley tees."),

# ---------- sport & snapbacks ----------
("sport","Bucks County Baseball Co.","https://buckscountybaseballco.com/collections/nhl-hats","Snapbacks · sports","30+ yrs","b","ask",
 "A card and memorabilia shop that has been in business <q>for over 30 years</q>. It lists 80s–90s Starter, Logo 7 and Sports Specialties caps, e.g. <q>PHILADELPHIA FLYERS VINTAGE NHL SNAPBACK HAT – DEADSTOCK $15</q>.",
 "Ask whether they hold multiple units of the $25 90s snapbacks."),
("sport","Bad Santa","https://shopbadsanta.com/collections/starter","Starter · snapbacks","unconfirmed","b","direct",
 "<b>Reseller</b>, but carries plenty of NWT: <q>Deadstock NWT Chicago Bulls 1997 NBA Champions Starter Snapback</q>, Quebec Nordiques Starter, <q>1990 NHL Hartford Whalers Starter T-Shirt</q>, NJ Devils 1995 Stanley Cup.",
 "Use the Starter collection. Expect resale prices."),
("sport","Premium32","https://premium32.com/collections/nhl-hats","Snapbacks","unconfirmed","c","direct",
 "<b>Reseller</b>. About 20 NHL snapbacks, e.g. <q>NHL All Star Game 1996 Boston Starter</q> and Senators script, plus Super Bowl XXVIII and 1995 All-Star caps.",
 "Condition isn't stated per item, so ask."),
("sport","Vintage Club Clothing","https://www.vintageclubclothing.com/collections/nfl","Sports tees · caps","unconfirmed","c","direct",
 "<b>Reseller</b>. 839 NFL items, some tagged Deadstock: Houston Oilers AJD snapback, Tennessee Oilers inaugural 1997 tee, Logo 7 Browns × Bart Simpson 1990.",
 "Search for \"deadstock\" within the store."),
("sport","RetroStar","https://www.retrostar.com.au/search?q=deadstock+t-shirt","Sports · bands (Australia)","2002","b","direct",
 "<b>Reseller</b>. A search for deadstock t-shirt returns 693 results, including <q>DEADSTOCK 1998 Mark McGwire</q>, <q>DEADSTOCK 2007 Arizona Diamondbacks</q> and <q>DEADSTOCK 1999 REM Tour</q>.",
 "Many results are from after 2010, so check the year in each title."),
("sport","The Captain's Vintage","https://thecaptainsvintage.com/collections/vintage-professional-wrestling-apparel","Wrestling","1998","c","direct",
 "(search index) <b>Reseller</b>, <q>Since 1998</q>. Listed <q>90s nWo WCW Wrestling Deadstock t-shirt</q> at $179.99.",
 "Check the wrestling collection."),
]

# ---------- hats ----------
S += [
("hats","CS80 Vintage","https://cs80vintage.squarespace.com/shop/hats","Snapbacks · fitteds","1960s store, online 2021","a","direct",
 "Stock from the closed Continental Sports store in Sacramento, which <q>stayed exactly where it was left, undisturbed for nearly 20 years</q>. <q>Every piece is original, unworn… true deadstock</q>. A 2026 podcast describes <q>thousands of hats</q>. The hats page lists 150+ caps, including defunct teams: Washington Bullets, Montreal Expos, Houston Oilers, Colt .45s fitted and LA Rams Super Bowl 1984.",
 "Drops go up Wednesday and Sunday at 8am PT. Use the team filter for defunct franchises. Mostly 70s–80s, and pricey."),
("hats","Cozy Vintage","https://cozyvintage.stores.jp","Novelty &amp; promo snapbacks (Japan)","unconfirmed","b","wholesale",
 "Lists many <b>DEADSTOCK</b> 80s–90s trucker caps and snapbacks at ¥3,520–4,950: an embroidered <q>'Car 54, Where Are You?'</q> TV cap, <q>OPERATION DESERT STORM</q>, DuPont Stren, Grinnell and Vibra-Pro. They <q>卸売りをしています</q> (sell wholesale) to dealers.",
 "Email info@used-cozy.com for a wholesale lot. A Japanese shop, but they sell in bulk to dealers."),
("hats","Bucks County Baseball Co.","https://buckscountybaseballco.com/collections/nhl-hats","Snapbacks","30+ yrs","b","ask",
 "A card and memorabilia shop in business <q>for over 30 years</q>. It lists 80s–90s Starter, Logo 7 and Sports Specialties caps, e.g. <q>PHILADELPHIA FLYERS VINTAGE NHL SNAPBACK HAT – DEADSTOCK $15</q>, plus Tampa Bay Lightning script caps and LOE bucket hats.",
 "Ask whether they hold multiple units of the $15–25 snapbacks."),
("hats","Bad Santa","https://shopbadsanta.com/collections/starter","Starter snapbacks","unconfirmed","b","direct",
 "<b>Reseller</b>, but carries plenty of NWT: <q>Deadstock NWT Chicago Bulls 1997 NBA Champions Starter Snapback</q>, a Green Bay Packers Miller Time promo snapback, Quebec Nordiques Starter and NJ Devils 1995 Stanley Cup.",
 "Use the Starter collection. Expect resale prices."),
("hats","Premium32","https://premium32.com/collections/nhl-hats","Snapbacks","unconfirmed","c","direct",
 "<b>Reseller</b>. About 20 snapbacks, e.g. <q>NHL All Star Game 1996 Boston Starter</q>, Capitals Sports Specialties, Senators script, Super Bowl XXVIII 1994.",
 "Condition isn't stated per item, so ask."),
]

# ---------- comic-shop round 2 ----------
S += [
("pop","Planet X","https://www.eplanetx.net/sandmanivtshirt.html","Comics · Vertigo · Image (Toronto)","1992","a","direct",
 "A comic and toy shop <q>in operation since 1992</q>, selling its own shop stock through an old Yahoo store, priced in USD. In stock: Graphitti <q>Sandman IV</q> double-sided tee (XXL), Graphitti <q>Arabian Nights Sandman</q> (XL), Sirius Poison Elves <q>Ebola Zaire</q> (1997, XL), a <q>Batman Forever Double-Sided</q> tee (1995, L), a Changes Superman logo tee and a Free Comic Book Day 2009 tee. Sold out but still listed: Marvel 1994 Generation X, Gen 13, Sin City <q>Blam Blam Blam</q>, which shows what they carried. Their own words: <q>Our webstore sells a fraction of the items we have available.</q>",
 "Check the Sin City, Hellboy, Chaos! Comics, Image and DC/Vertigo categories, and search the site for \"T-Shirt\". Email contact@eplanetx.net about the unlisted shop stock."),
("call","Kevin Eastman Studios","https://fan.kevineastmanstudios.com/shop/","TMNT · Mirage era","unconfirmed","c","ask",
 "Has a <q>Classic TMNT – Vintage Overstock</q> section (26 items) and <q>From the Personal Collections of Peter Laird and Kevin Eastman</q> (50 items of 80s–90s Mirage material, many factory sealed). The product lists load by script, so I couldn't see whether any Mirage-era tees are among them. The \"1984\" tees for sale are new reprints.",
 "Email them asking whether any original Mirage Studios tees are in the overstock."),
("call","Graham Crackers Comics","https://grahamcrackers.com","Comics (13 stores, IL/WI/CA)","1980s","c","ask",
 "A 13-store chain whose pages list <q>T-SHIRTS</q> and whole-store sales. Its site search loads by script, so I couldn't check the stock.",
 "A chain this size with stores this old likely has a back room of old Previews tees. Call and ask."),
("pop","Emory's Memories","https://www.emorysmemories.com/websale/miscellaneous.htm","Collectibles","unconfirmed","c","direct",
 "Lists a <q>BATMAN &amp; ROBIN T-SHIRT: Vintage New, Unused – still sealed in the original bag… Graphitti Designs shirt from the early-1990s</q>. Only one piece was seen.",
 "Small. Ask whether more sealed shirts came in with it."),
]

# ---------- toy/collectible round ----------
S += [
("dead","Official Store Wholesale (Old Glory's wholesale side)","https://officialstore.com/products/rock-band-guitar-head-soft-t-shirt","Cartoons · anime · games · movies","Old Glory-era","a","direct",
 "Same inventory as oldglory.com (shared SKUs, barcodes and photos) but at <b>wholesale prices, $7–13 a tee</b>, with exact counts per size. It claims <q>over 100,000 unique, in-stock items</q>. Old stock in quantity: Rock Band <q>Guitar Head</q> (2007–08) S 15 / M 121 / XL 46 / 2XL 57; Samurai 7 (c. 2005) S 33 / M 19; Aqua Teen DVD art juniors 50 / 13 / 26; Sealab 2021 (2000–05); Foster's Home for Imaginary Friends (2004–09); Dr. Horrible (2008). There are also mid-2000s licenses like Happy Bunny, Paris Hilton and Jolt.",
 "Search officialstore.com/search?q= and a show name: Sealab, Harvey Birdman, Hero 108, Fruits Basket, Mashimaro, Happy Tree Friends, Emily the Strange. This is the best bulk source on the list."),
("pop","Old Glory &amp; Stylin Online: how to find their old stock","https://stylinonline.com/collections/vendors?q=Changes","Your examples","2000s","a","direct",
 "You know these two already, but both still carry 2000s stock that's easy to miss. <b>Old Glory:</b> add <code>.js</code> to any product URL to see exact units, e.g. Family Guy <q>Bring It On</q> juniors M 34, plus a Stewie tee with an old-format barcode. <b>Stylin Online:</b> the maker pages show <b>257 in-stock items by Changes</b> and <b>301 by Ripple Junction</b>, both 2000s licensees. In stock: Family Guy <q>Weak Powers</q> (2007 Blue Harvest) all sizes $7.99, Borat <q>Wee Waa</q> (2006), Guitar Hero III youth (2007), Battlestar Galactica <q>Frack Me</q> youth $3.99.",
 "On Stylin, open /collections/vendors?q=Changes (also q=Ripple and q=Headline) and set Availability to In stock. Anything marked down to $3.99–9.99 is clearance dead stock. On Old Glory, filter collections to In stock and check the .js counts. Lower 5-digit SKUs look older."),
("pop","eStarland","https://www.estarland.com/product-description/AnimeMerchandise/Death-Jr-Head-T-Shirt-X-Large/24651","Anime · games","unconfirmed","b","direct",
 "(search index) An old game and anime shop with low product IDs. Listings include <q>Death Jr. Head T-Shirt X-Large – $4.95</q> (a 2005 PSP game), <q>Inu Yasha Parchment Background… Previews Exclusive T-Shirt</q> (listed as New), an InuYasha Dragon tee, Hellsing Alucard, Rurouni Kenshin and <q>Marvel vs Capcom</q> tees.",
 "Google <code>site:estarland.com \"T-Shirt\"</code> plus a title, and check stock in your own browser, because the site blocks bots."),
]

# ---------- convention round 2 ----------
S += [
("call","Who North America","https://www.whona.com/CLEARANCEPROMOS_c_139.html","Doctor Who · UK TV","1998","b","ask",
 "A US Doctor Who dealer since 1998 with its own warehouse, which still sells <b>1980s FASA Doctor Who miniatures in quantity</b> (e.g. FASA 9507: <q>536 available</q>) in its clearance section. A shop sitting on hundreds of units of 80s stock likely has old apparel too, but none is listed online.",
 "Email them about back-stock Doctor Who, Red Dwarf and Blake's 7 tees."),
("call","Doctor Who Store (Alien Entertainment)","https://www.doctorwhostore.com/vintage/","Doctor Who · fan club","1980s","c","ask",
 "Runs the Chicago TARDIS convention. Its <q>vintage</q> section sells unsold 1980s Doctor Who Fan Club of America buttons, a 1985 promo button, 1996 TV-movie TARDIS keys and 1999 Dalek plaques. Only 2 tees are online, both from after 2010.",
 "Ask them about leftover fan-club and convention shirts from the 80s and 90s."),
("call","Filmwelt","https://filmwelt-shop.com","Star Trek (Germany)","unconfirmed","c","direct",
 "A German Star Trek dealer selling out-of-production Lincoln Enterprises / Roddenberry pins, plus single-size tees such as <q>Vulcan Ale</q> and a <q>Captain Kirk</q> name shirt. The tees' age isn't stated.",
 "Ask for the print year. Small."),
]

# User asked for no sports and no Japanese resellers.
S = [r for r in S if r[0] not in ("japan","sport") and r[1] != "Mandarake"]

SECTIONS = [
 ("dead","Warehouse finds &amp; unsold stock","The strongest leads: unsold original stock in volume, sold by the company that made or stocked it."),
 ("pop","Comics, movies, TV, anime back-stock","Retailers with old licensed tees still in their catalog. They're smaller than the warehouse finds, but they're the original sellers."),
 ("call","Warehouses to call or email","Most of their old stock isn't listed online. Ask them directly what they have."),
 ("hats","Hats &amp; snapbacks","Deadstock caps from closed stores and old shops. Sports-team caps are included here because you asked for hats."),
 ("music","Band &amp; music","Old record and memorabilia shops with deadstock band tees."),
]
DROPPED = (
 "<b>Now only new or reprinted merch:</b> Creation Entertainment, Highspots, mycomicshop, Mile High Comics, TFAW, Midtown, Forbidden Planet, Fantagraphics, SLG, Fright-Rags, The Who Shop, Liquid Blue, EMP, Nuclear Blast, Impericon, MerchNow, Grindstore, Fun.com.<br>"
 "<b>From the last list, where you found little old stock:</b> 80sTees, BuyCoolShirts, Rocker Rags, Rock-n-Roll GangStar, Angry Young and Poor, eDeadShop, Metal-shop.eu, Heavy Metal Online, TruffleShuffle, Tracks, Backstage Auctions.<br>"
 "<b>Too little old stock:</b> Recordmecca (one shirt), Ebullition, Abstract Studio, Creation Xena tees, Entertainment Earth and Atomic Empire (old Graphitti tees all sold out).<br>"
 "<b>No tees at all:</b> Larry Edmunds, Dark Delicacies, Hake's, Bud's Art Books, Chuck Jones Gallery, Animazing, Clampett.<br>"
 "<b>Dead or parked domains:</b> interpunk, loudclothing, rocksax, artrock, hollywoodbookandposter, superheroden, oldschoolskates (\"coming soon\"), merchandisingplaza, concertshirts, metalshirts.<br>"
 "<b>Removed at your request:</b> sports tees and jerseys (Classic Football Shirts, Vintage Club Clothing, RetroStar) and Japanese resale shops (LABORATORY, DEAD STOCK TOKYO, Green Heaven, Bear's Choice, Disk Union, BerBerJin, Beat Bomb). Cozy Vintage stays in the hats section because it wholesales deadstock caps."
)
LV = {"a":("Strong","a"),"b":("Worth a look","b"),"c":("Small / ask","c")}
HOW = {"direct":"Buy online","proxy":"Via proxy","wholesale":"Wholesale acct","ask":"Contact them"}

def row(r):
    _,name,url,kind,since,lvl,how,ev,dig = r
    l,c = LV[lvl]
    src = ' <span class="src">search index</span>' if ev.startswith("(search index)") else ""
    ev = ev.replace("(search index) ","")
    return (f'<tr data-l="{lvl}"><td class="name"><a href="{html.escape(url)}" target="_blank" rel="noopener">{name}</a>'
            f'<small>{kind}</small><span class="since">since {since}</span></td>'
            f'<td class="ev"><span class="lvl {c}">{l}</span><span class="how">{HOW[how]}</span>{src}<p>{ev}</p></td>'
            f'<td class="look">{dig}</td></tr>')

def build():
    n = len(S); strong = sum(r[5]=="a" for r in S)
    tpl = pathlib.Path(__file__).with_name("oldstock_template.html").read_text()
    body = "".join(
        f'<section id="{sid}"><h2>{t} <span class="n">{sum(r[0]==sid for r in S)}</span></h2><p class="why">{why}</p>'
        f'<div class="tablewrap"><table><thead><tr><th>Store</th><th>What I found</th><th>Where to dig</th></tr></thead><tbody>'
        + "".join(row(r) for r in S if r[0]==sid) + "</tbody></table></div></section>"
        for sid,t,why in SECTIONS)
    nav = "".join(f'<a href="#{sid}">{t.split(" (")[0]}</a>' for sid,t,_ in SECTIONS)
    out = tpl.replace("__N__",str(n)).replace("__STRONG__",str(strong)).replace("__NAV__",nav).replace("__BODY__",body).replace("__DROPPED__",f'<section id="dropped"><h2>Checked &amp; dropped</h2><div class="box">{DROPPED}</div></section>')
    p = pathlib.Path(__file__).resolve().parent.parent/"output"/"leftover_stock_stores.html"
    p.write_text(out); print(n, "stores,", strong, "strong ->", p)

if __name__ == "__main__":
    build()
