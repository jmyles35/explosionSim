$(document).ready(function () {
    if (!Detector.webgl) {
        // Will not work unless browser supports WebGL
        Detector.addGetWebGLMessage();
        document.getElementById('container').innerHTML = "";
    }

    // Texture width for simulation -- 32 SEEMS OPTIMAL
    var WIDTH = 32;
    var NUM_TEXELS = WIDTH * WIDTH;

    // Size in system units
    var BOUNDS = WIDTH * 4;
    var BOUNDS_HALF = BOUNDS * 0.5;

    // Size in terms of number of vertices
    var SIZE = BOUNDS_HALF - 1;
    var HALF_SIZE = SIZE / 2;

    var DEFAULT_FIELD = 0;
    var DENSITY_FIELD = 1;
    var TEMPERATURE_FIELD = 2;
    var PRESSURE_FIELD = 3;
    var displayField = 0;

    var container, stats;
    var camera, scene, renderer, controls;
    var mouseMoved = false;
    var mouseCoords = new THREE.Vector2();
    var raycaster = new THREE.Raycaster();

    var waterMesh;
    var sphereMesh;
    var boxMesh;
    var meshRay;

    var gpuCompute;
    var heightmapVariable;
    var waterUniforms;
    var smoothShader;

    var simplex = new SimplexNoise();

    var windowHalfX = window.innerWidth / 2;
    var windowHalfY = window.innerHeight / 2;

    var colors = []; // Need for gradient

    var timeStep = 0;
    var TIME_DIV_FACTOR = 2;
    var DATA_SIZE = Object.keys(window.arrData).length;

    init();
    animate();
    console.log("Test Data:");
    console.log(window.objData[0][0][0]['T']);
    console.log("Data Size:");
    console.log(DATA_SIZE);


    /*
     * Initialize camera, scene, and inital renders.
     * Setup GUI, mouse interaction, initalize "water" and interactivity.
     */
    function init() {

        container = document.createElement( 'div' );
        document.body.appendChild( container );

        // Initalize Camera/Scene
        camera = new THREE.PerspectiveCamera( 80, window.innerWidth / window.innerHeight, 1, 3000 );
        camera.position.set( 0, 150, 0);
        scene = new THREE.Scene();

        // Lighting for our scene (we need this)
        var sun1 = new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
        sun1.position.set( 100, 200, 100 );
        scene.add( sun1 );
        var sun2 = new THREE.DirectionalLight( 0xFFFFFF, 0.6 );
        sun2.position.set( -100, 200, -100 );
        scene.add( sun2 );

        // Render WebGL
        renderer = new THREE.WebGLRenderer();
        renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize( window.innerWidth, window.innerHeight );
        container.appendChild( renderer.domElement );

        // Set controls for camera interaction
        controls = new THREE.OrbitControls( camera, renderer.domElement );

        // Adding events for user interactivity (I think)...
        document.addEventListener( 'mousemove', onDocumentMouseMove, false );
        document.addEventListener( 'touchstart', onDocumentTouchStart, false );
        document.addEventListener( 'touchmove', onDocumentTouchMove, false );

        // Toggle wireframe when key W is pressed.
        document.addEventListener( 'keydown', function( event ) {
            if ( event.keyCode === 87 ) {

                waterMesh.material.wireframe = ! waterMesh.material.wireframe;
                waterMesh.material.needsUpdate = true;

                sphereMesh.material.wireframe = ! sphereMesh.material.wireframe;
            }

        } , false );

        window.addEventListener( 'resize', onWindowResize, false );

        var gui = new dat.GUI();

        stats = new Stats();
        document.body.appendChild( stats.dom );

        var effectController = {
            sphereRadius: 10,
            boxSide: 15,
            timeFactor: 0.1
        };

        var geometryChanger = function() {

            var newRadius = effectController.sphereRadius;
            sphereMesh.geometry = new THREE.SphereGeometry( newRadius, 16, 16 );

            TIME_DIV_FACTOR = 1 / effectController.timeFactor;
        };

        gui.add( effectController, "sphereRadius", 1.0, 100.0, 1.0 ).onChange( geometryChanger );
        gui.add( effectController, "timeFactor", 0.1, 2, 0.1 ).onChange( geometryChanger );

        // Buttons for toggling the various propagations (temp, pressure, vel, density)
        var buttonDensity = {
            DensityField: function() {
                displayField = 1;
            }
        };
        var buttonTemp = {
            TemperatureField: function() {
                displayField = 2;
            }
        };
        var buttonPres = {
            PressureField: function() {
                displayField = 3;
            }
        };
        var buttonSphere = {
            ToggleSphere: function() {
                sphereMesh.material.visible = ! sphereMesh.material.visible;
            }
        };

        // Add buttons to the GUI.
        gui.add( buttonDensity, 'DensityField' );
        gui.add( buttonPres, 'PressureField' );
        gui.add( buttonTemp, 'TemperatureField' );
        gui.add( buttonSphere, 'ToggleSphere' );

        initWater();

        initSphere();
    }

    function initWater() {

        var geometry = new THREE.PlaneBufferGeometry( BOUNDS, BOUNDS, WIDTH - 1, WIDTH - 1 );

        // Initializing the colors
        for ( var i = 0; i <= HALF_SIZE; i++ ) {
            var y = i - HALF_SIZE;

            for ( var j = 0; j <= HALF_SIZE; j++ ) {

                colors.push( 0, 0, 1.0 );
            }
        }

        // Add 'color' to possible attributes of geometry
        geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colors, 3 ) );
        geometry.getAttribute( 'color' ).setDynamic(true);

        // Water material
        var material = new THREE.ShaderMaterial( {
            uniforms: THREE.UniformsUtils.merge( [
                THREE.ShaderLib[ 'phong' ].uniforms,
                {
                    heightmap: { value: null }
                }
            ] ),
            vertexShader: document.getElementById( 'waterVertexShader' ).textContent,
            fragmentShader: THREE.ShaderChunk[ 'meshphong_frag' ],
            vertexColors: THREE.VertexColors

        } );

        material.lights = true;

        // Material attributes from MeshPhongMaterial
        material.color = new THREE.Color( 0xFFFFFF );
        material.specular = new THREE.Color( 0x111111 );
        material.shininess = 0;

        // Sets the uniforms with the material values
        material.uniforms.diffuse.value = material.color;
        material.uniforms.specular.value = material.specular;
        material.uniforms.shininess.value = Math.max( material.shininess, 1e-4 );
        material.uniforms.opacity.value = material.opacity;

        // Defines
        material.defines.WIDTH = WIDTH.toFixed( 1 );
        material.defines.BOUNDS = BOUNDS.toFixed( 1 );
        waterUniforms = material.uniforms;

        // Water mesh
        waterMesh = new THREE.Mesh( geometry, material );
        waterMesh.rotation.x = - Math.PI / 2;
        waterMesh.matrixAutoUpdate = false;
        waterMesh.updateMatrix();

        scene.add( waterMesh );


        // Mesh just for mouse raycasting
        var geometryRay = new THREE.PlaneBufferGeometry( BOUNDS, BOUNDS, 1, 1 );
        meshRay = new THREE.Mesh( geometryRay, new THREE.MeshBasicMaterial( { color: 0xFFFFFF, visible: false } ) );
        meshRay.rotation.x = - Math.PI / 2;
        meshRay.matrixAutoUpdate = false;
        meshRay.updateMatrix();
        scene.add( meshRay );

        // Creates the gpu computation class and sets it up
        gpuCompute = new GPUComputationRenderer( WIDTH, WIDTH, renderer );

        var heightmap0 = gpuCompute.createTexture();

        fillTexture( heightmap0 );

        heightmapVariable = gpuCompute.addVariable( "heightmap", document.getElementById( 'heightmapFragmentShader' ).textContent, heightmap0 );

        gpuCompute.setVariableDependencies( heightmapVariable, [ heightmapVariable ] );

        heightmapVariable.material.uniforms.mousePos = { value: new THREE.Vector2( 10000, 10000 ) };
        heightmapVariable.material.uniforms.explosionSize = { value: 20.0 };
        heightmapVariable.material.uniforms.viscosityConstant = { value: 0.03 };
        heightmapVariable.material.defines.BOUNDS = BOUNDS.toFixed( 1 );

        var error = gpuCompute.init();

        if ( error !== null ) {
            console.error( error );
        }

        // Create compute shader to smooth the water surface and velocity
        var heightmap_flat = gpuCompute.createTexture();
        smoothShader = gpuCompute.createShaderMaterial( document.getElementById( 'smoothFragmentShader' ).textContent, { texture: heightmap_flat } );
    }

    function initSphere() {

        var geometry = new THREE.SphereGeometry( 10, 32, 32 );
        var material = new THREE.MeshPhongMaterial();
        material.visible = false;

        sphereMesh = new THREE.Mesh( geometry, material );

        scene.add( sphereMesh );
    }

    function fillTexture( texture ) {

        var waterMaxHeight = 50;

        function noise( x, y, z ) {
            var multR = waterMaxHeight/25;
            var mult = 0.025;
            var r = 0;
            for ( var i = 0; i < 15; i++ ) {
                r += multR * simplex.noise( x * mult, y * mult );
                multR *= 0.53 + 0.025 * i;
                mult *= 1.25;
            }
            return r;
        }

        var pixels = texture.image.data;

        var p = 0;
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {

                var x = i * 128 / WIDTH;
                var y = j * 128 / WIDTH;

                pixels[ p + 0 ] = noise( x, y, 123.4 );
                pixels[ p + 1 ] = 0;
                pixels[ p + 2 ] = 0;
                pixels[ p + 3 ] = 1;

                p += 4;
            }
        }
    }

    /*
     * Assign density to heights
     */
    function densityTexture( texture, time ) {

        var pixels = texture.image.data;

        var p = 0;
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {

                var height = window.arrData[time][i][j]['p'] * 5;

                pixels[ p + 0 ] = height;
                pixels[ p + 1 ] = height;
                pixels[ p + 2 ] = height;
                pixels[ p + 3 ] = height;

                p += 4;
            }
        }
    }

    /*
     * Assign temperature to heights
     */
    function temperatureTexture( texture, time ) {

        var pixels = texture.image.data;

        var p = 0;
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {

                var height = window.arrData[time][i][j]['T'] * 5;

                pixels[ p + 0 ] = height;
                pixels[ p + 1 ] = height;
                pixels[ p + 2 ] = height;
                pixels[ p + 3 ] = height;

                p += 4;
            }
        }
    }

    /*
     * Assign pressure to heights
     */
    function pressureTexture( texture, time ) {

        var pixels = texture.image.data;

        var p = 0;
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {

                var height = window.arrData[time][i][j]['P'] * 10;

                pixels[ p + 0 ] = height;
                pixels[ p + 1 ] = height;
                pixels[ p + 2 ] = height;
                pixels[ p + 3 ] = height;

                p += 4;
            }
        }
    }

    /*
     * Maps DENSITY values to specific COLORS on the mesh.
     * GREEN = HIGH, BLUE = LOW (can change color schemes).
     */
    function DensityField( time ) {

        var waterColor = waterMesh.geometry.getAttribute('color');
        waterColor.needsUpdate = true;
        var count = 0;

        // Iterate through each PRESSURE value, map to a color, and write color to mesh.
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {
                var color = getColourDensity(window.arrData[time][i][j]['p'], 2, 0);

                waterColor.setX(count, color[0]);
                waterColor.setY(count, color[1]);
                waterColor.setZ(count, color[2]);
                count++;
            }
        }
    }

    /*
     * Maps PRESSURE values to specific COLORS on the mesh
     * GREEN = HIGH, BLUE = LOW (can change color schemes).
     */
     function PressureField( time ) {

       var waterColor = waterMesh.geometry.getAttribute('color');
       waterColor.needsUpdate = true;
       var count = 0;

       // Iterate through each PRESSURE value, map to a color, and write color to mesh.
       for ( var i = 0; i < WIDTH; i++ ) {
           for ( var j = 0; j < WIDTH; j++ ) {
               var color = getColourPressure(window.arrData[time][i][j]['P'], 2, 0);

               waterColor.setX(count, color[0]);
               waterColor.setY(count, color[1]);
               waterColor.setZ(count, color[2]);
               count++;
           }
       }
     }

    /*
     * Maps TEMPERATURE values to specific COLORS on the mesh.
     * RED = HIGH, BLUE = LOW (can change color schemes).
     */
    function TemperatureField( time ) {

        var waterColor = waterMesh.geometry.getAttribute('color');
        waterColor.needsUpdate = true;
        var count = 0;

        // Iterate through each PRESSURE value, map to a color, and write color to mesh.
        for ( var i = 0; i < WIDTH; i++ ) {
            for ( var j = 0; j < WIDTH; j++ ) {
                var color = getColourTemperature(window.arrData[time][i][j]['T'], 2, 0);

                waterColor.setX(count, color[0]);
                waterColor.setY(count, color[1]);
                waterColor.setZ(count, color[2]);
                count++;
            }
        }
    }

    /*
     * Functions for adjusting window SIZE
     */
    function onWindowResize() {

        windowHalfX = window.innerWidth / 2;
        windowHalfY = window.innerHeight / 2;

        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize( window.innerWidth, window.innerHeight );
    }


    function setMouseCoords( x, y ) {

        mouseCoords.set( ( x / renderer.domElement.clientWidth ) * 2 - 1, - ( y / renderer.domElement.clientHeight ) * 2 + 1 );
        mouseMoved = true;
    }

    function onDocumentMouseMove( event ) {

        setMouseCoords( event.clientX, event.clientY );
    }

    function onDocumentTouchStart( event ) {

        if ( event.touches.length === 1 ) {

            event.preventDefault();
            setMouseCoords( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY );
        }
    }

    function onDocumentTouchMove( event ) {

        if ( event.touches.length === 1 ) {

            event.preventDefault();
            setMouseCoords( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY );
        }
    }

    function animate() {

        requestAnimationFrame( animate );
        render();
        stats.update();

        if ( timeStep % TIME_DIV_FACTOR === 0 ) {
            var smallTime = timeStep / TIME_DIV_FACTOR;

            if (displayField === DENSITY_FIELD) DensityField( smallTime );
            if (displayField === TEMPERATURE_FIELD) TemperatureField ( smallTime );
            if (displayField === PRESSURE_FIELD) PressureField( smallTime );
            //if (displayField === VELOCITY_FIELD) VelocityField( smallTime );
        }
        // Pause if default
        if ( displayField != DEFAULT_FIELD ) {
            if ((timeStep + 1)/TIME_DIV_FACTOR < DATA_SIZE) timeStep++;
            else timeStep = 0;
        }
    }

    function render() {

        // Set uniforms: mouse interaction
        var uniforms = heightmapVariable.material.uniforms;

        // Do the gpu computation
        gpuCompute.compute();

        if (timeStep % TIME_DIV_FACTOR === 0 ) {

            var smallTime = timeStep / TIME_DIV_FACTOR;
            var heightmap = gpuCompute.createTexture();

            if (displayField === DENSITY_FIELD) densityTexture( heightmap, smallTime );
            if (displayField === TEMPERATURE_FIELD) temperatureTexture ( heightmap, smallTime );
            if (displayField === PRESSURE_FIELD) pressureTexture( heightmap, smallTime );

            waterUniforms.heightmap.value = heightmap;
            renderer.render( scene, camera );
        }
    }

   /*
    * INPUT: density (for a single vertex), maximum density, ambient density.
    *
    * REDDER = HIGH DENSITY, BLUER = LOW DENSITY.
    * densityMax and densityAir are taken as parameters but can be removed if we define
    * them as global constants at some point. For now they are arbitrary.
    *
    * RETURN: array containing RGB in [0], [1], [2]. Values between 0 and 2.
    */
    function getColourDensity( density, densityMax, densityAir ) {
      var densityRange = (densityMax - densityAir);
      var densityHalf = ( (densityMax + densityAir) / 2);

      var returnColor = [];

      // Colour initializations
      var red = 0;
      var green = 0;
      var blue = 0.1;

      // Computes values for red and blue
      // VALUES SHOULD BE BETWEEN 0 AND 2(?).
      if( density >= densityAir && density <= densityHalf ) {
        green = 1;
        // degree of "greenness" is increased in proportion to magnitude of density within given bounds.
        red = 1 * ( ( density - densityAir ) / ( densityMax / 2 - densityAir ) );

      } else if( density > densityHalf && density <= densityMax ) {
        red = 1;
        // degree of "blueness" decreased in proportion to magnitude of density within given bounds.
        green = 1 * ( (densityMax - density) / (densityMax - densityHalf) );

      } else if ( density > densityMax ) {
        red = 1;
        green = 0;
      }

      returnColor[0] = red;
      returnColor[1] = green;
      returnColor[2] = blue;

      return returnColor;

    }

    // Returns corresponding color representation for temperature.
    function getColourTemperature( temp, tempMax, tempAir ) {
      var tempRange = (tempMax - tempAir);
      var tempHalf = ( (tempMax + tempAir) / 2);

      var returnColor = [];

      // Colour initializations
      var red = 0;
      var green = 0.1;
      var blue = 0;

      // Computes values for red and blue
      // VALUES SHOULD BE BETWEEN 0 AND 2(?).
      if( temp >= tempAir && temp <= tempHalf ) {
        blue = 1;
        // degree of "greenness" is increased in proportion to magnitude of density within given bounds.
        red = 1 * ( ( temp - tempAir ) / ( tempMax / 2 - tempAir ) );

      } else if( temp > tempHalf && temp <= tempMax ) {
        red = 1;
        // degree of "blueness" decreased in proportion to magnitude of density within given bounds.
        blue = 1 * ( (tempMax - temp) / (tempMax - tempHalf) );

      } else if ( temp > tempMax ) {
        red = 1;
        blue = 0;
      }

      returnColor[0] = red;
      returnColor[1] = green;
      returnColor[2] = blue;

      return returnColor;

    }

    // Returns corresponding color representation for pressure.
    function getColourPressure( pres, presMax, presAir ) {
      var presRange = (presMax - presAir);
      var presHalf = ( (presMax + presAir) / 2);

      var returnColor = [];

      // Colour initializations
      var red = 0.1;
      var green = 0;
      var blue = 0;

      // Computes values for red and blue
      // VALUES SHOULD BE BETWEEN 0 AND 2(?).
      if( pres >= presAir && pres <= presHalf ) {
        blue = 1;
        // degree of "greenness" is increased in proportion to magnitude of pressure within given bounds.
        green = 1 * ( ( pres - presAir ) / ( presMax / 2 - presAir ) );

      } else if( pres > presHalf && pres <= presMax ) {
        green = 1;
        // degree of "blueness" decreased in proportion to magnitude of pressure within given bounds.
        blue = 1 * ( (presMax - pres) / (presMax - presHalf) );

      } else if ( pres > presMax ) {
        green = 1;
        blue = 0;
      }

      returnColor[0] = red;
      returnColor[1] = green;
      returnColor[2] = blue;

      return returnColor;

    }

});
