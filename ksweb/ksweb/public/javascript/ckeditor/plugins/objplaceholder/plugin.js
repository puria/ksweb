CKEDITOR.plugins.add( 'objplaceholder', {
    requires: 'widget',

    icons: 'objplaceholder',

    init: function( editor ) {
        CKEDITOR.dialog.add( 'objplaceholder', this.path + 'dialogs/objplaceholder.js' );

        editor.widgets.add( 'objplaceholder', {

            button: 'Create a simple obj placeholder',

            template:
                '<p class="objplaceholder ">output</p>',
            allowedContent:
                'p(objplaceholder)[id];',

            dialog: 'objplaceholder',


            downcast: function(el) {
                console.log("downcast", el);
                alert(el);
                return new CKEDITOR.htmlParser.text( '[[' + this.data.name + ']]' );
            },

            upcast: function( element ) {
                return element.name == 'p' && element.hasClass( 'objplaceholder' );
            }
        });
    }
} );