const toggleSidebarBtn = document.getElementById("toggleSidebar");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");
const historicoMsg = document.getElementById("histociomsg");
const newChat = document.getElementById("newChat");
const historicoChat = document.getElementById("historicochat");
const nomeUsuario = document.getElementById("nomeusuario");

const botMessages = [
    "Olá, eu sou um chatbot projetado para responder e resolver suas dúvidas sobre vacas, bois e outros temas relacionados!",
    "Olá, como posso ajudá-lo?",
    "Sim, entendi. Posso ajudá-lo com isso?",
    "Não entendi. Pode explicar melhor?",
    "Ok, vou verificar isso.",
    "Sim, é possível. Vou ajudá-lo a resolver isso."
];

toggleSidebarBtn.addEventListener("click", () => {
    const isSidebarCollapsed = sidebar.style.width === "0px" || sidebar.style.width === "0";

    sidebar.style.width = isSidebarCollapsed ? "250px" : "0";
    mainContent.style.marginLeft = isSidebarCollapsed ? "250px" : "0";
    toggleSidebarBtn.textContent = isSidebarCollapsed ? "Hide Sidebar" : "Show Sidebar";
    toggleSidebarBtn.innerHTML = '<i class="bi bi-list"></i>';

    nomeUsuario.style.transform = isSidebarCollapsed ? "translateY(-50%)" : "translateX(-200%) translateY(-50%)";
    historicoChat.style.transform = isSidebarCollapsed ? "translateY(0%)" : "translateX(-200%)";
    newChat.style.transform = isSidebarCollapsed ? "translateX(210%)" : "translateY(-20%)";
});

document.getElementById("sendBtn").addEventListener("click", () => {
    const chatInput = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");
    const message = chatInput.value.trim();

    let ultimaMensagem;
        const obterUltimaMensagem = (idchat) => {
    fetch(`/retornar_msgGEMINI?chat_id=${idchat}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        ultimaMensagem = '' + data.ultimaMsgG;
        console.log('Última mensagem:', ultimaMensagem);
    })
    .catch((error) => {
        console.error('Erro ao obter a última mensagem:', error);
    });
};
    if (message) {
        const chatId = parseInt(document.querySelector('meta[name="chat-id"]').getAttribute('content'), 10);
        const quantidade = parseInt(document.querySelector('meta[name="quantidade"]').getAttribute('content'), 10);

        const saveMessage = (content, origin, originbot) => {
    fetch('/save_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: content,
            chatId: chatId,
            origin: origin,
            originbot: originbot
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Mensagem salva:', data);
        const createMessageElement = (text, className) => {
            const messageElement = document.createElement("div");
            messageElement.textContent = text;
            messageElement.className = className;
            messageElement.style.wordWrap = "break-word";
            chatBox.appendChild(messageElement);
        };

        obterUltimaMensagem(chatId)
        setTimeout(() => {
            createMessageElement(message, "sent-message");
            chatInput.value = "";
            const botMessage = ultimaMensagem
            createMessageElement(botMessage, "received-message");
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 2000);

        if(chatId === 0){
            window.location.href = `/chatbot/${quantidade}`;
        }
    })
    .catch((error) => {
        console.error('Erro ao salvar a mensagem:', error);
    });
};
        saveMessage(message, 0, 1);
    }
});

document.getElementById("chat-input").addEventListener('keydown', (event) => {
    const chatInput = document.getElementById("chat-input");
    if (event.key === 'Backspace') {
        if (chatInput.value.length  === 1){
            chatInput.style.height = "5px";
        }
    }
    if (event.key === 'Enter') {
        if (event.shiftKey) {
            event.preventDefault();
            const cursorPosition = chatInput.selectionStart;
            chatInput.value = chatInput.value.slice(0, cursorPosition) + '\n' + chatInput.value.slice(cursorPosition);
            chatInput.selectionStart = chatInput.selectionEnd = cursorPosition + 1;
            chatInput.style.height = "60px";
        } else {
            event.preventDefault();
            document.getElementById("sendBtn").click();
        }
    }
});

document.querySelectorAll('.bi-pencil').forEach(icon => {
    icon.addEventListener('click', (event) => {
        if (icon.classList.contains('bi-trash')) {
            const chatId = icon.closest('li').dataset.chatId;
            enableDelete(icon, chatId);
        } else {
            const chatId = icon.closest('li').dataset.chatId;
            enableEditing(icon, chatId);
        }
    });
});

function enableEditing(pencilIcon, chatId) {
    event.preventDefault();
    const listItem = pencilIcon.closest('li');
    const chatName = listItem.querySelector('.chat-name');
    const editInput = listItem.querySelector('.edit-name-input');
    editInput.value = '';

    chatName.style.display = 'none';
    editInput.style.display = 'inline';
    editInput.focus();

   const handleEvent = function(event) {
        if (event.type === 'blur' || (event.type === 'keypress' && event.key === 'Enter')) {
            if (editInput.value.length === 0) {
                editInput.value = chatName.textContent
            }
            saveName(listItem, editInput, chatId);
        }
    };

    editInput.addEventListener('blur', handleEvent);
    editInput.addEventListener('keypress', handleEvent);
}

function saveName(listItem, editInput, chatId) {
    const chatName = listItem.querySelector('.chat-name');
    const newName = editInput.value;

    chatName.textContent = newName;
    chatName.style.display = 'inline';
    editInput.style.display = 'none';

    fetch('/rename_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            chatId: chatId,
            newName: newName
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Nome do chat salvo:', data);
    })
    .catch((error) => {
        console.error('Erro ao salvar o nome do chat:', error);
    });
}

function enableDelete(pencilIcon, chatIdex) {
    event.preventDefault();

    fetch('/excluir_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            chatId: chatIdex
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Chat Excluido:', data);
        window.location.href = '/chatbot';
    })
    .catch((error) => {
        console.error('Erro ao excluir o chat:', error);
    });
}