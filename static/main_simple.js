$(document).ready(function ()
{
    if (!Detector.webgl) {

        Detector.addGetWebGLMessage();
        document.getElementById('container').innerHTML = "";
    }

    var container = document.createElement( 'div' );

    var camera = new THREE.PerspectiveCamera( 80, window.innerWidth / window.innerHeight, 1, 3000 );
    var scene = new THREE.Scene();

    var sun1 = new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
    sun1.position.set( 100, 200, 100 );
    scene.add( sun1 );

    var renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    var material = new THREE.MeshNormalMaterial();
    var geometry = new THREE.SphereGeometry( 20, 128, 128 );

    var sphere = new THREE.Mesh( geometry, material );
    scene.add( sphere );

    function animate() {

        sphere.rotation.x += 0.5;
        requestAnimationFrame( animate );
        renderer.render( scene, camera );
    }
});
