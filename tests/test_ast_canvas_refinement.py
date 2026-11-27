"""WP03-AST-VISUAL-REFINE-001. Measure the production canvas in Edge."""

from test_ast_studio import (
    TELEMETRY, app_url, graph_model, import_large_graph, post_json, record, studio, upload,
)


def test_labels_and_replay_camera(studio):
    page = studio
    project = post_json(page, "/api/projects", {"name": "Camera and labels"})["id"]
    file = upload(page, project, "telemetry.py", TELEMETRY)
    page.goto("/workbench/projects")
    graph = graph_model(page, file["id"])
    result = page.evaluate("""async graph => {
        const {createCanvas} = await import('/static/ast-canvas.js');
        const canvas = document.createElement('canvas');
        canvas.style = 'position:fixed;inset:0;width:820px;height:550px';
        document.body.append(canvas);
        const ctx = canvas.getContext('2d');
        let labels, boxes, circles;
        for (const name of ['clearRect','arc','roundRect','fillText']) {
            const original = ctx[name].bind(ctx);
            ctx[name] = (...args) => {
                if (name === 'clearRect') { boxes = []; circles = []; labels = []; }
                if (name === 'roundRect') boxes.push(args.slice(0,4));
                if (name === 'arc' && args[3] === 0 && args[4] === 2*Math.PI) circles.push(args.slice(0,3));
                if (name === 'fillText' && args.length === 4) labels.push(args[0]);
                return original(...args);
            };
        }
        const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
        const clamp = (v,lo,hi) => Math.max(lo,Math.min(v,hi));
        let zoom = 0;
        const view = createCanvas(canvas, graph, {onZoom: scale => { zoom = Math.round(100*scale); }});
        view.setMotion(false);
        await frame();
        const output = {names:labels.length, labelHits:0, glyphHits:0};
        for (const [index, [x,y,w,h]] of boxes.entries()) {
            for (const [a,b,c,d] of boxes.slice(index+1)) {
                if (x < a+c && x+w > a && y < b+d && y+h > b) output.labelHits++;
            }
            for (const [cx,cy,r] of circles) {
                if (Math.hypot(cx-clamp(cx,x,x+w),cy-clamp(cy,y,y+h)) < r-.001) output.glyphHits++;
            }
        }
        // A wheel zoom about this anchor puts the file centre just 12 px outside
        // the left edge: its overscanned glyph used to keep a clamped nameplate.
        const root = graph.nodes[0];
        const initial = view.positionOf(root.id);
        view.select(root.id);
        view.zoom(3, (3*initial.x+12)/2, initial.y);
        await frame();
        output.rootX = Math.round(view.positionOf(root.id).x);
        output.offscreenLabel = labels.includes(root.name);
        output.initialZoom = zoom;
        view.setMotion(true);
        view.replay();
        // Pause strictly inside the camera movement, using actual rendered feedback.
        const deadline = performance.now()+2500;
        while (zoom >= output.initialZoom-3 && performance.now() < deadline) await frame();
        view.pause();
        await frame();
        output.pausedZoom = zoom;
        const frozen = canvas.toDataURL();
        await new Promise(resolve => setTimeout(resolve,350));
        output.stable = canvas.toDataURL() === frozen && output.pausedZoom === zoom;
        view.resume();
        await new Promise(resolve => setTimeout(resolve,750));
        output.finishedZoom = zoom;
        view.setMotion(false);
        view.zoom(2);
        canvas.style.width = '420px';
        canvas.style.height = '300px';
        await frame(); await frame();
        output.resizedZoom = zoom;
        view.replay();
        output.reducedZoom = zoom;
        view.destroy(); canvas.remove();
        return output;
    }""", graph)
    assert result["names"] >= 10 and result["labelHits"] == result["glyphHits"] == 0
    assert result["rootX"] == -12 and not result["offscreenLabel"]
    assert result["initialZoom"] == 300 and 100 < result["pausedZoom"] < 300
    assert result["stable"] and result["finishedZoom"] == result["reducedZoom"] == 100
    assert result["resizedZoom"] > 200
    record("REFINED_CAMERA_LABELS", result)


def test_terminal_family_layout(studio):
    page = studio
    file = import_large_graph(page)
    page.goto("/workbench/projects")
    graph = graph_model(page, file["id"])
    result = page.evaluate("""async graph => {
        const {createCanvas} = await import('/static/ast-canvas.js');
        const canvas = document.createElement('canvas');
        canvas.style = 'width:820px;height:550px';
        document.body.append(canvas);
        const view = createCanvas(canvas,graph);
        const root = view.positionOf(graph.nodes[0].id);
        const classes = graph.nodes.filter(n => n.type==='class');
        const tracks = classes.map(parent => new Set(graph.nodes.filter(n => n.parent_id===parent.id).map(n => {
            const p = view.positionOf(n.id);
            // Invert the radial layout's horizontal 1.18 aspect ratio.
            return Math.hypot((p.x-root.x)/1.18,p.y-root.y).toFixed(2);
        })).size);
        view.destroy(); canvas.remove();
        return {classes:classes.length,minTracks:Math.min(...tracks),maxTracks:Math.max(...tracks)};
    }""", graph)
    assert result == {"classes": 27, "minTracks": 3, "maxTracks": 3}
    record("TERMINAL_LAYOUT", result)
