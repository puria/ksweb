/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
    // Define changes to default configuration here. For example:
    // config.language = 'fr';
    config.uiColor = '#f1f1f1';
    config.extraPlugins = 'widget,lineutils,clipboard,widgetselection';
    config.allowedContent = true;

    config.toolbarGroups = [
        { name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
        { name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
        { name: 'forms', groups: [ 'forms' ] },
        { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
        { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
        { name: 'links', groups: [ 'links' ] },
        { name: 'insert', groups: [ 'insert' ] },
        { name: 'document', groups: [ 'mode', 'doctools', 'document' ] },
        '/',
        { name: 'styles', groups: [ 'styles' ] },
        { name: 'colors', groups: [ 'colors' ] },
        { name: 'tools', groups: [ 'tools' ] },
        { name: 'others', groups: [ 'others' ] },
        { name: 'about', groups: [ 'about' ] }
    ];

    config.removeButtons = 'Source,Save,Templates,Scayt,Form,HiddenField,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,About,Flash,Smiley,SpecialChar,PageBreak,Iframe,Anchor,Unlink,Link,Styles,ShowBlocks,Language,BidiRtl,BidiLtr,CreateDiv,Blockquote,CopyFormatting,RemoveFormat,Superscript,Subscript,Strike,Replace,Find,SelectAll,NewPage';
};
