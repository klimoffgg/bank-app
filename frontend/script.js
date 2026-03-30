const API_URL = 'http://localhost:8000';
async function createTransaction(sender, receiver, amount) {
    try {
        const response = await fetch(`${API_URL}/transactions`, {
            method: 'POST',
            body: JSON.stringify({
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }),
            headers: {
                'Content-Type': 'application/json'
            },
        });
        if (!response.ok) {
            throw new Error(`Неудачная попытка создания транзакции: ${response.status}`);
        }
        const data = await response.json();
        return data;
    }
    catch (error) {
        alert(`Error: ${error.message}`);
        throw error;
    }
}
async function getAllTransaction() {
    try {
        const response = await fetch(`${API_URL}/transactions`);
        if (!response.ok) {
            throw new Error(`Неудачаная попытка получить все транзакции: ${response.status}`);
        }
        const data = await response.json();
        return data;
    }
    catch (error) {
        alert(`Error: ${error.message}`);
        throw error;
    }
}
async function changeTransaction(id, newStatus) {
    try {
        const response = await fetch(`${API_URL}/transactions/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'status': newStatus
            })
        });
        if (!response.ok) {
            throw new Error(`Неудачаная попытка изменить транзакцию с id ${id}: ${response.status}`);
        }
        const data = await response.json();
        return data;
    }
    catch (error) {
        alert(`Error: ${error.message}`);
        throw error;
    }
}
async function deleteTransaction(id) {
    try {
        const response = await fetch(`${API_URL}/transactions/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error(`Неудачаная попытка удалить транзакцию с id ${id}: ${response.status}`);
        }
        console.log(`Транзакция ${id} успешно удалена`);
    }
    catch (error) {
        alert(`Error: ${error.message}`);
        throw error;
    }
}
const form_HMLFormElement = document.getElementById('transaction-form');
const tableBody_HTMLTableElement = document.getElementById('transactions-body');
async function renderTable() {
    try {
        const transactions = await getAllTransaction();
        tableBody_HTMLTableElement.innerHTML = '';
        transactions.forEach(tx => {
            const tr = document.createElement('tr');
            const badgeClass = `badge-${tx.status.toLowerCase()}`;
            tr.innerHTML = `
                <td>${tx.id}</td>
                <td>${tx.sender}</td>
                <td>${tx.receiver}</td>
                <td>${tx.amount} ₽</td>
                <td><span class="badge ${badgeClass}">${tx.status}</span></td>
                <td class="actions">
                    <button class="btn-action edit" onclick="handleEdit(${tx.id})">Изменить</button>
                    <button class="btn-action delete" onclick="handleDelete(${tx.id})">Удалить</button>
                </td>
            `;
            tableBody_HTMLTableElement.appendChild(tr);
        });
    }
    catch (error) {
        console.error("Ошибка при отрисовке таблицы:", error);
    }
}
const inputSender_HTMLInputElement = document.getElementById('sender');
const inputReceiver_HTMLInputElement = document.getElementById('receiver');
const inputAmount_HTMLInputElement = document.getElementById('amount');
form_HMLFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await createTransaction(inputSender_HTMLInputElement.value, inputReceiver_HTMLInputElement.value, Number(inputAmount_HTMLInputElement.value));
        form_HMLFormElement.reset();
        await renderTable();
    }
    catch (error) {
        alert(`Error: ${error.message}`);
        throw error;
    }
});
window.handleDelete = async (id) => {
    if (confirm(`Вы действительно хотите удалить транзакцию N ${id}?`)) {
        try {
            await deleteTransaction(id);
            await renderTable();
        }
        catch (error) {
            alert(`Error: ${error.message}`);
            throw error;
        }
    }
};
window.handleEdit = async (id) => {
    const newStatus = prompt("Введите новый статус (DRAFT, PROCESSING, FROZEN, ARCHIVE):");
    if (newStatus) {
        const upperStatus = newStatus.toUpperCase();
        const validStatuses = ['DRAFT', 'PROCESSING', 'FROZEN', 'ARCHIVE'];
        if (!validStatuses.includes(upperStatus)) {
            alert("Некорректный статус! Попробуйте еще раз.");
            return;
        }
        try {
            await changeTransaction(id, upperStatus);
            await renderTable();
        }
        catch (error) {
            console.error("Ошибка при обновлении:", error);
        }
    }
};
