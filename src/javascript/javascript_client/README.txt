
To see the client library in action, start your RESTx server
and go here:

    http://localhost:8001/static/restx/examples/restx_js_example_1.html


The JavaScript client library, examples and supporting
themes are located in the static_files/restx/ directory,
so that it is ready to be served by RESTx.

These are the individual files:

static_files/
    restx/
        scripts/
            restx_plugin.js             # The actual client library implementation
            jquery-1.4.2.min.js         # A copy of jQuery, which is used by the RESTx client library
            restx_js_client_example.js  # Shows usage examples of the client library
        examples/
            restx_js_example_1.html     # Example file, which loads and uses the RESTx JavaScript library
            restx_js_example_2.html     # Example file, which loads and uses the RESTx JavaScript library
        theme/
            combo.css                   # A css theme used by the examples

