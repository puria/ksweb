CKEDITOR.dialog.add( 'objplaceholder', function( editor ) {
    return {
        title: 'Modifiertrtrtca il placeholder',
        minWidth: 200,
        minHeight: 100,
        contents: [
            {
                id: 'info',
                elements: [
                    {
                        id: 'id',
                        type: 'text',
                        label: 'ID',
                        width: '100px',
                        setup: function( widget ) {
                        },
                        
                        commit: function( widget ) {
                            widget.element.setAttribute( 'id', this.getValue() );
                        }
                        
                    }
                ]
            }
        ]
    };
} );