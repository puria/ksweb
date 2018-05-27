Ractive.DEBUG = /unminified/.test(function(){/*unminified*/});

var KS = (function() {
    var _entityRegex = /(\\)?@@([^\W]+)\b/g;
    //var _entityRegex =  /\B(\\)?\${([^}]+)\b/g;
    //var _entityRegex =   /\${([^}]+)}/g;
    //var _entityRegex = new RegExp('\\\\\\$', 'g') //\$/g;

    var ajax = function(url, params, callback, fail=()=>{}) {
        $.ajax({
            type: 'POST',
            url: url,
            data: params,
            dataType: "json",
            processData: false,
            contentType: 'application/json'
        })
        .done(callback)
        .fail(function(jqXHR) {
              console.error(`FAILED call for ${url}: ${jQuery.parseJSON(jqXHR.responseText)}`);
              if(typeof fail === 'function') {
                  fail();
              }
        });
    }

    var editor = function(element) {
        var showdownExtensions = [
            {
                type: 'lang',
                regex: _entityRegex,
                replace: function (match, leadingSlash, entity) {
                    if (leadingSlash === '\\') {
                        return match;
                    } else {
                        var id = match.split(/([_\W])/)[4]
                        var title = $(`#${id} > span`).text()
                        var cls = (title) ? "badge-primary" : "badge-danger"
                        return `<span class="badge badge-pill ${cls} entity">${title||id}</span>`;
                    }
                }
            },
            // {
            //     type: 'lang',
            //     regex: '\\\\@',
            //     replace: '@'
            // }
        ];

        var converter = new showdown.Converter({
            emoji: true,
            table: true,
            simplifiedAutoLink: true,
            excludeTrailingPunctuationFromURLs: true,
            tables: true,
            tasklists: true,
            simpleLineBreaks: true,
            extensions: showdownExtensions,
        });

        return new SimpleMDE({ 
            element: element,
            renderingConfig: {
                singleLineBreaks: true
            },
            spellChecker: false,
            previewRender: function(text) {
                return converter.makeHtml(text);
            },
        });
    }

    var addEntityToEditor = function(id, editor) {
        editor.codemirror.replaceSelection(`@@${id}`+" ")
    }

    var getEntitiesList = function(text) {
        return text.match(_entityRegex) || []
    }

    return {
        ajax: ajax,
        editor: editor,
        getEntitiesList: getEntitiesList,
        addEntityToEditor: addEntityToEditor,
    }
})();