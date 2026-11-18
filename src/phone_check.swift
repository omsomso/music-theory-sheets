// Load the screen version of the sheet at phone width (390 px) in WebKit, fail if anything
// sticks out sideways, and save three PNG snapshots down the page for a visual check.
// Usage: phone_check <sheet-preview.html> <png-prefix> [dark] [closed]
// "closed" leaves expandable sections as they load instead of opening them all first.
import Cocoa
import WebKit

let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: phone_check sheet-preview.html png-prefix"); exit(2) }
let url = URL(fileURLWithPath: args[1])
let outPrefix = args[2]
let W: CGFloat = 390

final class Checker: NSObject, WKNavigationDelegate {
    var web: WKWebView!
    var win: NSWindow!

    func start() {
        web = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: 800))
        web.appearance = NSAppearance(named: args.dropFirst(3).contains("dark") ? .darkAqua : .aqua)
        win = NSWindow(contentRect: NSRect(x: -20000, y: -20000, width: W, height: 800),
                       styleMask: [.borderless], backing: .buffered, defer: false)
        win.contentView = web
        win.orderBack(nil)
        web.navigationDelegate = self
        web.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
    }

    func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { self.measure() }
    }

    func measure() {
        // Open every expandable section first so its content is measured and photographed too.
        let openAll = args.dropFirst(3).contains("closed") ? "false" : "true"
        let js = """
        (document.querySelectorAll('details').forEach(function (d) { if (\(openAll)) d.open = true; }),
        JSON.stringify({
          vw: innerWidth,
          docW: document.documentElement.scrollWidth,
          h: document.documentElement.scrollHeight,
          wide: [...document.querySelectorAll('.srow,.arow,.erow,.mrow,.xrow,.whitemodes,.card,.mel,.chrom,.top,.notes2,.cells,h1,.legend,summary,.sec-controls')]
            .filter(e => e.getBoundingClientRect().right > innerWidth + 1)
            .map(e => e.className + ':' + Math.round(e.getBoundingClientRect().right)).slice(0, 12)
        }))
        """
        web.evaluateJavaScript(js) { r, _ in
            guard let s = r as? String,
                  let o = try? JSONSerialization.jsonObject(with: Data(s.utf8)) as? [String: Any] else {
                print("could not read page state"); exit(1)
            }
            print(s)
            let vw = o["vw"] as? Int ?? 0
            let docW = o["docW"] as? Int ?? 0
            let wide = o["wide"] as? [String] ?? []
            let h = CGFloat(o["h"] as? Int ?? 3000)
            self.snap([0, h * 0.3, h * 0.75], ok: docW <= vw && wide.isEmpty)
        }
    }

    func snap(_ tops: [CGFloat], ok: Bool, _ i: Int = 0) {
        if i == tops.count {
            if ok { print("phone width: OK, nothing sticks out"); exit(0) }
            print("ERROR: content is wider than the phone screen"); exit(3)
        }
        let full = max(tops.last! + 800, 800)
        web.frame = NSRect(x: 0, y: 0, width: W, height: full)
        win.setContentSize(NSSize(width: W, height: full))
        let c = WKSnapshotConfiguration()
        c.rect = CGRect(x: 0, y: tops[i], width: W, height: 760)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            self.web.takeSnapshot(with: c) { img, _ in
                if let img = img, let t = img.tiffRepresentation, let rep = NSBitmapImageRep(data: t),
                   let png = rep.representation(using: .png, properties: [:]) {
                    try? png.write(to: URL(fileURLWithPath: "\(outPrefix)-\(i + 1).png"))
                }
                self.snap(tops, ok: ok, i + 1)
            }
        }
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let checker = Checker()
checker.start()
DispatchQueue.main.asyncAfter(deadline: .now() + 40) { print("timeout"); exit(1) }
app.run()
