// render.jsx: build a layered banner PSD in Photoshop from a layout JSON written by build.py.
// Run: osascript -e 'tell application "Adobe Photoshop 2026" to do javascript file "<this>" with arguments {"<layout.json>"}'
#target photoshop
function cid(s) { return charIDToTypeID(s); }
function sid(s) { return stringIDToTypeID(s); }
function rgb(hex) { var c = new ActionDescriptor(); var n = parseInt(hex.replace("#", ""), 16);
    c.putDouble(cid("Rd  "), (n >> 16) & 255); c.putDouble(cid("Grn "), (n >> 8) & 255); c.putDouble(cid("Bl  "), n & 255); return c; }
function solid(hex) { var c = new SolidColor(); c.rgb.hexValue = hex.replace("#", ""); return c; }
function readJSON(path) { var f = new File(path); f.encoding = "UTF-8"; f.open("r"); var s = f.read(); f.close(); return eval("(" + s + ")"); }

function setFx(fx) {
    if (!fx) return;
    var d = new ActionDescriptor(), ref = new ActionReference();
    ref.putProperty(cid("Prpr"), cid("Lefx")); ref.putEnumerated(cid("Lyr "), cid("Ordn"), cid("Trgt"));
    d.putReference(cid("null"), ref);
    var e = new ActionDescriptor(); e.putUnitDouble(cid("Scl "), cid("#Prc"), 100);
    if (fx.shadow) { var s = fx.shadow, ds = new ActionDescriptor();
        ds.putBoolean(cid("enab"), true); ds.putEnumerated(cid("Md  "), cid("BlnM"), cid("Mltp"));
        ds.putObject(cid("Clr "), cid("RGBC"), rgb(s.color || "#000000"));
        ds.putUnitDouble(cid("Opct"), cid("#Prc"), s.opacity); ds.putBoolean(cid("uglg"), false);
        ds.putUnitDouble(cid("lagl"), cid("#Ang"), s.angle || 90); ds.putUnitDouble(cid("Dstn"), cid("#Pxl"), s.distance);
        ds.putUnitDouble(cid("Ckmt"), cid("#Pxl"), s.spread || 0); ds.putUnitDouble(cid("blur"), cid("#Pxl"), s.size);
        ds.putBoolean(cid("AntA"), true); ds.putBoolean(sid("layerConceals"), true);
        e.putObject(cid("DrSh"), cid("DrSh"), ds); }
    if (fx.glow) { var g = fx.glow, og = new ActionDescriptor();
        og.putBoolean(cid("enab"), true); og.putEnumerated(cid("Md  "), cid("BlnM"), cid("Scrn"));
        og.putObject(cid("Clr "), cid("RGBC"), rgb(g.color)); og.putUnitDouble(cid("Opct"), cid("#Prc"), g.opacity);
        og.putEnumerated(cid("GlwT"), cid("BETE"), cid("SfBL")); og.putUnitDouble(cid("Ckmt"), cid("#Pxl"), g.spread || 0);
        og.putUnitDouble(cid("blur"), cid("#Pxl"), g.size); og.putUnitDouble(cid("Nose"), cid("#Prc"), 0);
        og.putUnitDouble(cid("ShdN"), cid("#Prc"), 0); og.putBoolean(cid("AntA"), true);
        og.putUnitDouble(cid("Inpr"), cid("#Prc"), 50);
        e.putObject(cid("OrGl"), cid("OrGl"), og); }
    if (fx.stroke) { var k = fx.stroke, st = new ActionDescriptor();
        st.putBoolean(cid("enab"), true);
        st.putEnumerated(cid("Styl"), cid("FStl"), cid(k.position == "inside" ? "InsF" : (k.position == "center" ? "CtrF" : "OutF")));
        st.putEnumerated(cid("PntT"), cid("FrFl"), cid("SClr")); st.putEnumerated(cid("Md  "), cid("BlnM"), cid("Nrml"));
        st.putUnitDouble(cid("Opct"), cid("#Prc"), k.opacity || 100); st.putUnitDouble(cid("Sz  "), cid("#Pxl"), k.size);
        st.putObject(cid("Clr "), cid("RGBC"), rgb(k.color));
        e.putObject(cid("FrFX"), cid("FrFX"), st); }
    d.putObject(cid("T   "), cid("Lefx"), e);
    executeAction(cid("setd"), d, DialogModes.NO);
}

function roundRect(doc, it) {
    var d = new ActionDescriptor(), ref = new ActionReference();
    ref.putClass(sid("contentLayer")); d.putReference(cid("null"), ref);
    var d2 = new ActionDescriptor(), d3 = new ActionDescriptor();
    d3.putObject(cid("Clr "), cid("RGBC"), rgb(it.color)); d2.putObject(cid("Type"), sid("solidColorLayer"), d3);
    var r = new ActionDescriptor(), px = cid("#Pxl");
    r.putUnitDouble(sid("unitValueQuadVersion"), cid("#Prc"), 1);
    r.putUnitDouble(cid("Top "), px, it.y); r.putUnitDouble(cid("Left"), px, it.x);
    r.putUnitDouble(cid("Btom"), px, it.y + it.h); r.putUnitDouble(cid("Rght"), px, it.x + it.w);
    var rad = it.r || 0;
    r.putUnitDouble(sid("topRight"), px, rad); r.putUnitDouble(sid("topLeft"), px, rad);
    r.putUnitDouble(sid("bottomLeft"), px, rad); r.putUnitDouble(sid("bottomRight"), px, rad);
    d2.putObject(cid("Shp "), cid("Rctn"), r);
    d.putObject(cid("Usng"), sid("contentLayer"), d2);
    executeAction(cid("Mk  "), d, DialogModes.NO);
    var L = doc.activeLayer; L.name = it.name || "panel";
    if (it.fill_opacity != null) L.fillOpacity = it.fill_opacity;
    if (it.opacity != null) L.opacity = it.opacity;
    setFx(it.fx); return L;
}

function placeImage(doc, it) {
    var src = app.open(new File(it.file));
    var L = src.activeLayer.duplicate(doc, ElementPlacement.PLACEATBEGINNING);
    src.close(SaveOptions.DONOTSAVECHANGES);
    app.activeDocument = doc; doc.activeLayer = L;
    var b = L.bounds; L.translate(it.x - b[0].as("px"), it.y - b[1].as("px"));
    L.name = it.name || "image";
    if (it.rotate) L.rotate(it.rotate, AnchorPosition.MIDDLECENTER);
    if (it.opacity != null) L.opacity = it.opacity;
    if (it.blend) L.blendMode = eval("BlendMode." + it.blend);
    setFx(it.fx); return L;
}

function addText(doc, it) {
    // point text: (x, baseline) anchors the first line; justification is around x
    var L = doc.artLayers.add(); L.kind = LayerKind.TEXT; L.name = it.name || it.text.substr(0, 30);
    var t = L.textItem; t.kind = TextType.POINTTEXT;
    t.contents = it.text.replace(/\n/g, "\r");
    t.font = it.font; t.size = new UnitValue(it.size, "px");
    t.color = solid(it.color);
    t.justification = it.justify == "center" ? Justification.CENTER : (it.justify == "right" ? Justification.RIGHT : Justification.LEFT);
    if (it.tracking) t.tracking = it.tracking;
    if (it.leading) { t.useAutoLeading = false; t.leading = new UnitValue(it.leading, "px"); }
    t.position = [new UnitValue(it.x, "px"), new UnitValue(it.baseline, "px")];
    if (it.opacity != null) L.opacity = it.opacity;
    setFx(it.fx); return L;
}

function buildBanner(spec) {
    app.preferences.rulerUnits = Units.PIXELS; app.preferences.typeUnits = TypeUnits.PIXELS;
    app.displayDialogs = DialogModes.NO;
    // Build at 72 ppi so px text sizes and paragraph boxes are exact, then retag the resolution.
    var doc = app.documents.add(spec.width, spec.height, 72, spec.name, NewDocumentMode.RGB, DocumentFill.TRANSPARENT);
    var parents = [doc];
    function walk(items, parent) {
        for (var i = 0; i < items.length; i++) {
            var it = items[i];
            if (it.type == "group") {
                var g = parent.layerSets.add(); g.name = it.name;
                g.move(parent, ElementPlacement.PLACEATBEGINNING);
                doc.activeLayer = g;
                walk(it.items, g);
                continue;
            }
            var L;
            if (it.type == "rect") L = roundRect(doc, it);
            else if (it.type == "image") L = placeImage(doc, it);
            else if (it.type == "text") L = addText(doc, it);
            if (L) L.move(parent, ElementPlacement.PLACEATBEGINNING);   // later items paint on top
        }
    }
    walk(spec.items, doc);
    // drop the empty layer the transparent document came with
    var last = doc.layers[doc.layers.length - 1];
    if (last.typename == "ArtLayer" && last.name == "Layer 1") last.remove();
    doc.resizeImage(undefined, undefined, spec.dpi, ResampleMethod.NONE);
    var psd = new PhotoshopSaveOptions(); psd.layers = true; psd.embedColorProfile = true;
    doc.saveAs(new File(spec.out_psd), psd, true);
    var jpg = new JPEGSaveOptions(); jpg.quality = 11; jpg.embedColorProfile = true;
    doc.saveAs(new File(spec.out_jpg), jpg, true);
    doc.close(SaveOptions.DONOTSAVECHANGES);
    return "ok " + spec.name;
}

var __args = (typeof arguments != "undefined" && arguments.length) ? arguments : null;
buildBanner(readJSON(__args ? __args[0] : "/tmp/layout.json"));
