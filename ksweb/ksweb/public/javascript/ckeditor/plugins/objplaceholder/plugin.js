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
                var classes = el.attributes.class.split(" ");
                var downcast_value = '';
                for (var i=0; i<classes.length; i++)
                    if (classes[i].startsWith('ks_id-'))
                        downcast_value = classes[i].slice('ks_id-'.length);

                return new CKEDITOR.htmlParser.text( '${' + downcast_value + '}' );
            },

            upcast: function( element ) {
                return element.name == 'span' && element.hasClass( 'objplaceholder' );
            }
        });
    }
} );