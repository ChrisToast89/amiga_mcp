// winid <owner-substring> — print the CGWindowID of the largest window whose owner matches
import CoreGraphics
let want = CommandLine.arguments[1].lowercased()
let l = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
var best: (Int, Double) = (0, 0)
for w in l {
    let o = ((w["kCGWindowOwnerName"] as? String) ?? "").lowercased()
    guard o.contains(want), let b = w["kCGWindowBounds"] as? [String: Double] else { continue }
    let a = (b["Width"] ?? 0) * (b["Height"] ?? 0)
    if a > best.1 { best = ((w["kCGWindowNumber"] as? Int) ?? 0, a) }
}
print(best.0)
