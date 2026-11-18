// Render fixed-size .page sections of an HTML file to a multi-page PDF (595x842 pt each) with WebKit,
// and export a PNG preview of every page.
// Usage: render <in.html> <out.pdf> <png-prefix>
import Cocoa
import PDFKit
import WebKit

let args = CommandLine.arguments
guard args.count >= 4 else { print("usage: render in.html out.pdf png-prefix"); exit(2) }
let htmlURL = URL(fileURLWithPath: args[1])
let pdfURL = URL(fileURLWithPath: args[2])
let pngPrefix = args[3]
let W: CGFloat = 595
let H: CGFloat = 842

final class Renderer: NSObject, WKNavigationDelegate {
    var web: WKWebView!
    var window: NSWindow!
    var overflowing = false

    func start() {
        let cfg = WKWebViewConfiguration()
        web = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H), configuration: cfg)
        web.appearance = NSAppearance(named: .aqua)
        window = NSWindow(contentRect: NSRect(x: -20000, y: -20000, width: W, height: H),
                          styleMask: [.borderless], backing: .buffered, defer: false)
        window.contentView = web
        window.orderBack(nil)
        web.navigationDelegate = self
        web.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { poll(0) }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("load failed: \(error)"); exit(1)
    }

    func poll(_ tries: Int) {
        let js = """
        JSON.stringify({
          s: document.fonts.status,
          fams: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v,i,a) => a.indexOf(v) === i),
          n: document.querySelectorAll('.page').length,
          over: [...document.querySelectorAll('.page')].map(p => p.scrollHeight - p.clientHeight),
          wide: [...document.querySelectorAll('.page')].map(p => p.scrollWidth - p.clientWidth),
          used: [...document.querySelectorAll('.page')].map(p => Math.ceil(
            p.lastElementChild.getBoundingClientRect().bottom - p.getBoundingClientRect().top
            + parseFloat(getComputedStyle(p).paddingBottom)))
        })
        """
        web.evaluateJavaScript(js) { res, _ in
            guard let str = res as? String,
                  let obj = try? JSONSerialization.jsonObject(with: Data(str.utf8)) as? [String: Any] else {
                print("could not read page state"); exit(1)
            }
            if (obj["s"] as? String) != "loaded" && tries < 150 {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { self.poll(tries + 1) }
                return
            }
            print("fonts loaded: \(obj["fams"] ?? "?")")
            print("overflow px per page (height): \(obj["over"] ?? "?")")
            print("overflow px per page (width):  \(obj["wide"] ?? "?")")
            let used = (obj["used"] as? [Int] ?? []).map(String.init).joined(separator: ", ")
            print("height used per page (of \(Int(H)) px): \(used)")
            let over = (obj["over"] as? [Int] ?? []) + (obj["wide"] as? [Int] ?? [])
            self.overflowing = over.contains { $0 > 0 }
            if (obj["s"] as? String) != "loaded" { print("warning: web fonts did not finish loading") }
            let n = obj["n"] as? Int ?? 0
            self.window.setContentSize(NSSize(width: W, height: H * CGFloat(n)))
            self.web.frame = NSRect(x: 0, y: 0, width: W, height: H * CGFloat(n))
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { self.capture(n) }
        }
    }

    func capture(_ n: Int) {
        let doc = PDFDocument()
        func step(_ i: Int) {
            if i == n {
                doc.write(to: pdfURL)
                for p in 0..<doc.pageCount {
                    guard let page = doc.page(at: p) else { continue }
                    let img = page.thumbnail(of: NSSize(width: W * 2, height: H * 2), for: .mediaBox)
                    if let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
                       let png = rep.representation(using: .png, properties: [:]) {
                        try? png.write(to: URL(fileURLWithPath: "\(pngPrefix)-\(p + 1).png"))
                    }
                }
                print("wrote \(doc.pageCount) pages to \(pdfURL.path)")
                if self.overflowing {
                    print("ERROR: content does not fit its A4 page (see overflow above)")
                    exit(3)
                }
                exit(0)
            }
            let c = WKPDFConfiguration()
            c.rect = CGRect(x: 0, y: CGFloat(i) * H, width: W, height: H)
            web.createPDF(configuration: c) { result in
                switch result {
                case .success(let data):
                    if let d = PDFDocument(data: data), let p = d.page(at: 0) { doc.insert(p, at: doc.pageCount) }
                case .failure(let e):
                    print("pdf failed: \(e)"); exit(1)
                }
                step(i + 1)
            }
        }
        step(0)
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let renderer = Renderer()
renderer.start()
DispatchQueue.main.asyncAfter(deadline: .now() + 60) { print("timeout"); exit(1) }
app.run()
