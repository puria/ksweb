CKEDITOR.plugins.add( 'objplaceholder', {
    requires: 'widget',

    icons: 'objplaceholder',

    init: function( editor ) {
        CKEDITOR.dialog.add( 'objplaceholder', this.path + 'dialogs/objplaceholder.js' );

        editor.widgets.add( 'objplaceholder', {

            button: 'Create a simple obj placeholder',

            template:
                '<span class="objplaceholder ">output</span>',
            allowedContent:
                'span(*)[id];',

            dialog: 'objplaceholder',


            downcast: function(el) {

                var ractive_instance;

                if (typeof ractive_output !== 'undefined') {
                    ractive_instance = ractive_output;
                } else if (typeof ractive_document !== 'undefined'){
                    ractive_instance = ractive_document;
                } else {
                    console.log("ERROR: unexpected ractive template!");
                    return;
                }

                var type_ = '';
                var id_ = '';
                var downcast_value = '';


                if (el.hasClass( 'qa-widget' )){
                    type_ = 'qa_response'
                } else if (el.hasClass( 'output-widget' )){
                    type_ = 'output';
                } else {
                    console.log("ERROR: unexpected widget class!");
                    return;
                }

                var classes = el.attributes.class.split(" ");

                for (var i=0; i<classes.length; i++)
                    if (classes[i].startsWith('ks_id-')){
                        downcast_value = classes[i].slice('ks_id-'.length);
                        id_ =  downcast_value.split('_')[1];
                        break;
                }

                ractive_instance.get('create.content').push({
                    'type': type_,
                    'content': id_,
                    'title': el.children[0].value
                });

                //TODO: escape chars...
                return new CKEDITOR.htmlParser.text( '${' + downcast_value + '}' );
            },

            upcast: function( element ) {
                return element.name == 'span' && element.hasClass( 'objplaceholder' );
            }
        });
    }
} );