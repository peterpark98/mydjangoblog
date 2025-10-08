document.addEventListener("DOMContentLoaded", function () {
    // --- 主题切换 ---
    const themeSwitch = document.getElementById('themeSwitch');
    const darkPrismTheme = document.getElementById('prism-dark-theme');
    const lightPrismTheme = document.getElementById('prism-light-theme');

    function applyTheme(theme) {
        if (theme === 'light-mode') {
            document.body.classList.add('light-mode');
            if(themeSwitch) themeSwitch.innerHTML = '<i class="fas fa-moon"></i>';
            if (darkPrismTheme && lightPrismTheme) {
                darkPrismTheme.disabled = true;
                lightPrismTheme.disabled = false;
            }
        } else {
            document.body.classList.remove('light-mode');
            if(themeSwitch) themeSwitch.innerHTML = '<i class="fas fa-sun"></i>';
            if (darkPrismTheme && lightPrismTheme) {
                darkPrismTheme.disabled = false;
                lightPrismTheme.disabled = true;
            }
        }
        
        if (typeof Prism !== 'undefined' && document.querySelector('.ck-editor') === null) {
            Prism.highlightAll();
        }
    }

    const savedTheme = localStorage.getItem('theme') || 'dark-mode';
    if (savedTheme === 'light-mode') {
        if(themeSwitch) themeSwitch.innerHTML = '<i class="fas fa-moon"></i>';
    } else {
        if(themeSwitch) themeSwitch.innerHTML = '<i class="fas fa-sun"></i>';
    }

    if (themeSwitch) {
        themeSwitch.addEventListener('click', () => {
            let currentTheme = document.body.classList.contains('light-mode') ? 'light-mode' : 'dark-mode';
            let newTheme = currentTheme === 'light-mode' ? 'dark-mode' : 'light-mode';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }

    // --- 滚动加载动画 ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // --- 个人中心 "只读/编辑" 模式切换 ---
    const displayView = document.getElementById('profile-display-view');
    const editView = document.getElementById('profile-edit-view');
    const editBtn = document.getElementById('edit-profile-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    if (displayView && editView && editBtn && cancelBtn) {
        editBtn.addEventListener('click', function() {
            displayView.style.display = 'none';
            editView.style.display = 'block';
        });
        cancelBtn.addEventListener('click', function() {
            editView.style.display = 'none';
            displayView.style.display = 'block';
        });
    }

    // --- 自动隐藏消息提示 ---
    const messageAlerts = document.querySelectorAll('.messages-container .alert');
    messageAlerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 3000);
    });

    document.querySelectorAll('.reply-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const commentId = this.dataset.commentId;
            const username = this.dataset.username;
            
            // 直接通过 ID 找到对应的回复表单容器，这是最可靠的方式
            const formContainer = document.querySelector(`#reply-form-container-${commentId}`);

            // 获取主评论表单及其所有需要操作的元素
            const mainFormContainer = document.querySelector('#main-comment-form-container');
            const commentForm = document.querySelector('#commentForm');
            const parentIdInput = document.querySelector('#parentId');
            const commentTextarea = commentForm.querySelector('textarea');
            const commentFormTitle = document.querySelector('#comment-form-title');

            // 安全检查，确保所有元素都已找到
            if (!formContainer || !mainFormContainer || !commentForm) {
                console.error("评论表单或其容器未找到，无法执行回复操作。");
                return;
            }

            // 判断是打开还是关闭回复框
            const isAlreadyOpen = formContainer.style.display === 'block';

            // 1. 先关闭所有已打开的回复框，并将主表单归位
            document.querySelectorAll('.reply-form-container').forEach(container => {
                if (container.style.display === 'block') {
                    container.style.display = 'none';
                    mainFormContainer.appendChild(commentForm);
                    parentIdInput.value = '';
                    commentFormTitle.textContent = '发表评论';
                    commentTextarea.placeholder = '';
                }
            });

            // 2. 如果刚才点击的回复框是关闭的，则打开它
            if (!isAlreadyOpen) {
                formContainer.appendChild(commentForm); // 将主表单移动到当前回复框
                parentIdInput.value = commentId;        // 设置父评论ID
                commentFormTitle.textContent = `回复 @${username}`; // 更新标题
                commentTextarea.placeholder = `回复 @${username}...`; // 更新占位符
                formContainer.style.display = 'block'; // 显示回复框
                commentTextarea.focus(); // 自动聚焦
            }
        });
    });

    // --- 头像裁剪和预览功能 ---
    const modalElement = document.getElementById('cropImageModal');
    if (modalElement) {
        const imageInput = document.getElementById('id_image');
        const modal = new bootstrap.Modal(modalElement);
        const imageToCrop = document.getElementById('imageToCrop');
        const cropButton = document.getElementById('crop-button');
        const imagePreview = document.getElementById('image-preview');
        let cropper;

        modalElement.setAttribute('inert', '');

        imageInput.addEventListener('change', function (e) {
            const files = e.target.files;
            if (files && files.length > 0) {
                const file = files[0];
                const reader = new FileReader();
                reader.onload = function (event) {
                    imageToCrop.src = event.target.result;
                    imageToCrop.onload = () => {
                        modalElement.removeAttribute('inert');
                        modal.show();
                    };
                    imageToCrop.onerror = () => {
                        alert('图片加载失败，请选择有效的图片文件。');
                        modal.hide();
                    };
                };
                reader.readAsDataURL(file);
            }
        });

        modalElement.addEventListener('shown.bs.modal', function () {
            cropButton.disabled = true;
            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: 'move',
                background: false,
                autoCropArea: 0.8,
                ready: function () {
                    cropButton.disabled = false;
                },
            });
        });

        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.setAttribute('inert', '');
            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
        });

        cropButton.addEventListener('click', function () {
            if (!cropper) {
                alert('裁剪工具未初始化，请重试。');
                return;
            }

            const cropData = cropper.getData(true); 
            document.getElementById('id_x').value = cropData.x;
            document.getElementById('id_y').value = cropData.y;
            document.getElementById('id_width').value = cropData.width;
            document.getElementById('id_height').value = cropData.height;

            const canvas = cropper.getCroppedCanvas({ width: 300, height: 300 });
            if (!canvas) {
                alert('无法生成裁剪图像，请确保已选择有效区域。');
                return;
            }

            imagePreview.src = canvas.toDataURL('image/jpeg');

            canvas.toBlob(function(blob) {
                const fileInput = document.getElementById('id_image');
                const newFile = new File([blob], 'cropped_image.jpg', { type: 'image/jpeg' });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;

                cropButton.blur();
                modal.hide();
            }, 'image/jpeg');
        });
    }

    // --- 代码块自定义头部和折叠功能 ---
    const contentBody = document.querySelector('.content-body');
    if (contentBody) {
        const pres = contentBody.querySelectorAll('pre');
        pres.forEach(pre => {
            pre.classList.add('line-numbers', 'word-wrap');
        });

        setTimeout(() => {
            const codeToolbars = contentBody.querySelectorAll('div.code-toolbar');
            
            codeToolbars.forEach(toolbarContainer => {
                const pre = toolbarContainer.querySelector('pre');
                if (!pre || toolbarContainer.querySelector('.code-block-header')) {
                    return;
                }
                
                const header = document.createElement('div');
                header.className = 'code-block-header';

                const language = pre.className.match(/language-(\S+)/)?.[1] || '';
                const languageTag = document.createElement('span');
                languageTag.className = 'language-tag';
                languageTag.textContent = language;

                const controls = document.createElement('div');
                controls.className = 'controls';

                const copyButton = document.createElement('button');
                copyButton.textContent = '复制';
                copyButton.addEventListener('click', () => {
                    const code = pre.querySelector('code').innerText;
                    navigator.clipboard.writeText(code).then(() => {
                        copyButton.textContent = '复制成功!';
                        copyButton.classList.add('copied');
                        setTimeout(() => {
                            copyButton.textContent = '复制';
                            copyButton.classList.remove('copied');
                        }, 2000);
                    });
                });
                
                const collapseButton = document.createElement('button');
                collapseButton.textContent = '折叠';
                collapseButton.addEventListener('click', () => {
                    const container = toolbarContainer.closest('.code-block-container');
                    container.classList.toggle('collapsed');
                    if (container.classList.contains('collapsed')) {
                        collapseButton.textContent = '展开';
                    } else {
                        collapseButton.textContent = '折叠';
                    }
                });
                
                controls.appendChild(copyButton);
                controls.appendChild(collapseButton);
                header.appendChild(languageTag);
                header.appendChild(controls);

                const container = document.createElement('div');
                container.className = 'code-block-container';
                toolbarContainer.parentNode.insertBefore(container, toolbarContainer);
                container.appendChild(header);
                container.appendChild(toolbarContainer);
            });

            if (typeof Prism !== 'undefined') {
                Prism.highlightAll();
            }
        }, 100);
    }
    
    // 1. 找到评论表单
    const commentForm = document.querySelector('#commentForm.prevent-double-submit');
    
    // 2. 如果表单存在，则只为它绑定一次 'submit' 事件监听器
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            // 找到表单内的提交按钮
            const submitButton = commentForm.querySelector('.submit-btn');
            
            // 如果按钮存在且已被禁用，则阻止本次提交
            if (submitButton && submitButton.disabled) {
                e.preventDefault();
                return;
            }

            // 如果按钮存在，则禁用它并更改文本
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = '提交中...';
            }
        });
    }
});