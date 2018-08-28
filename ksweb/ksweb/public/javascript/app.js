Ractive.DEBUG = /unminified/.test(function(){/*unminified*/});

var KS = (function() {
    var _entityRegex = /(\\)?@@([^\W]+)\b/g;
    var _answerRegex = /(\\)?%%([^\W]+)\b/g;

    var ajax = function(url, params, callback, fail) {
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
              console.error('FAILED call for', url, jqXHR.responseText);
              if (typeof fail === 'function') {
                  fail(jqXHR);
              }
        });
    }

    var getTitle = function(id) {
        return $(`#${id} > span`).text()
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
                        var title = getTitle(id)
                        var cls = (title) ? "badge-primary" : "badge-danger"
                        return `<span class="badge badge-pill ${cls} entity">${title||id}</span>`;
                    }
                }
            },
            {
                type: 'lang',
                regex: '\\\\@',
                replace: '@'
            },
            {
                type: 'lang',
                regex: _answerRegex,
                replace: function (match, leadingSlash, entity) {
                    if (leadingSlash === '\\') {
                        return match;
                    } else {
                        var id = match.split(/([_\W])/)[4]
                        var title = getTitle(id)
                        var cls = (title) ? "badge-success" : "badge-danger"
                        return `<span class="badge badge-pill ${cls} entity">${title||id}</span>`;
                    }
                }
            },

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

    var addOutputToEditor = function(id, editor) {
        editor.codemirror.replaceSelection(`@@${id} `)
    }

    var addAnswerToEditor = function (id, editor) {
        editor.codemirror.replaceSelection(`%%${id} `)
    }

    var getEntitiesList = function(text) {
        return text.match(_entityRegex) || []
    }

    return {
        ajax: ajax,
        editor: editor,
        getEntitiesList: getEntitiesList,
        addOutputToEditor: addOutputToEditor,
        addAnswerToEditor: addAnswerToEditor,
        getTitle: getTitle,
    }
})();