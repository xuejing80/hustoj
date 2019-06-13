$(function () {
    // var csrfitems = $('input[name ="csrfmiddlewaretoken"]');
    var csrftoken = $('input[name ="csrfmiddlewaretoken"]').val();

    window.deseditor = new Simditor({
        textarea: $('#editor'),
        placeholder: "问题的详细描述...",
        upload: {
            url: '/wenda/upload/media/qusImg',
            params: { csrfmiddlewaretoken: csrftoken },
            fileKey: 'img',
            connectionCount: 3,
            leaveConfirm: '正在上传问题，确定要离开吗？'
        },
        pasteImage: true,
        cleanPaste: true,
        // autosave: 'editor-content',
        toolbar:
        [
            'bold',
            'italic',
            'underline',
            'fontScale',
            'code',           
            'link',
            'image',
            'hr',            
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