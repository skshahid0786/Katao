let model;

(async function() {
    const app = new PIXI.Application({ autoStart: true, resizeTo: window, transparent: true, antialias: true });
    document.getElementById('live2d-container').appendChild(app.view);

    try {
        // Loads your model straight from your local files
        model = await PIXI.live2d.Live2DModel.from('/static/live2d_models/hiyori/Hiyori.model3.json');
        app.stage.addChild(model);
        
        setupLayout();
    } catch(e) { 
        console.warn("Live2D file loading check:", e); 
    }

    function setupLayout() {
        if(!model) return;
        const scale = window.innerWidth > 800 ? 0.45 : 0.28;
        model.scale.set(scale);
        model.anchor.set(0.5, 1);
        model.x = window.innerWidth / 2;
        model.y = window.innerHeight;
    }

    window.addEventListener('resize', setupLayout);
    window.addEventListener('mousemove', e => model?.focus(e.clientX, e.clientY));
})();

