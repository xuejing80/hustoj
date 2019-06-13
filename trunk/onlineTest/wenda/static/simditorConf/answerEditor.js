$(function () {
    // var csrfitems = $('input[name ="csrfmiddlewaretoken"]');
    var csrftoken = $('input[name ="csrfmiddlewaretoken"]').val();

    window.anseditor = new Simditor({
        textarea: $('#editor'),
        placeholder: "快写下你的答案吧...",
        upload: {
            url: '/wenda/upload/media/answerImg',
            params: { csrfmiddlewaretoken: csrftoken },
            fileKey: 'img',
            connectionCount: 3,
            leaveConfirm: 'Uploading is in progress, are you sure to leave this page?'
        },
        pasteImage: true,
        cleanPaste: true,
        // autosave: 'editor-content',
        toolbar:
        [
            'title',
            'bold',
            'italic',
            'underline',
            'strikethrough',
            'fontScale',
            'ol' ,          
            'ul',             
            'blockquote',
            'code',           
            'link',
            'image',
            'hr',            
            'indent',
            'outdent',
            'alignment',
        ],
        // toolbarHidden:false,
        // allowedTags: ['br', 'span', 'a', 'img', 'b', 'strong', 'i', 'strike', 'u', 'font', 'p', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'hr'],
        codeLanguages:
        [
            { name: 'Java', value: 'java' },
            { name: 'C++', value: 'c++' },
            { name: 'C#', value: 'cs' },
            { name: 'PHP', value: 'php' },
            { name: 'Python', value: 'python' },
            { name: 'JavaScript', value: 'js' },
            { name: 'CSS', value: 'css' },
            { name: 'HTML,XML', value: 'html' },
            { name: 'Markdown', value: 'markdown' },
            { name: 'Objective C', value: 'oc' },
            { name: 'SQL', value: 'sql' },
            { name: 'Bash', value: 'bash' },
        ],
    });
    // anseditor = editor;
})
