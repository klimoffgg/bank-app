const API_URL = '/api';

interface Transaction {
    id: number;
    sender: string;
    receiver: string;
    amount: number;
    status: string;
}

async function createTransaction(sender: string, receiver: string, amount:number): Promise<Transaction>{
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

        if (!response.ok){
            throw new Error(`Неудачная попытка создания транзакции: ${response.status}`);
        }

        const data = await response.json();
        return data as Transaction;
    } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }
}

async function getAllTransaction():Promise<Transaction[]>{
    try{
        const response: Response = await fetch(`${API_URL}/transactions`);

        if (!response.ok){
            throw new Error(`Неудачаная попытка получить все транзакции: ${response.status}`);
        }

        const data = await response.json()
        return data as Transaction[]
    } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }   
}

async function changeTransaction(id: number, newStatus: string): Promise<Transaction>{
    try{
        const response = await fetch(`${API_URL}/transactions/${id}`,{
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'status': newStatus
            })
    })

    if (!response.ok){
            throw new Error(`Неудачаная попытка изменить транзакцию с id ${id}: ${response.status}`);
        }
    const data = await response.json()
    return data as Transaction

    } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }   
}

async function deleteTransaction(id: number): Promise<void> {
    try{
        const response = await fetch(`${API_URL}/transactions/${id}`,{
            method: 'DELETE'
        })
        if (!response.ok){
            throw new Error(`Неудачаная попытка удалить транзакцию с id ${id}: ${response.status}`);
        }

        console.log(`Транзакция ${id} успешно удалена`);
    } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }   
}


const form_HMLFormElement = document.getElementById('transaction-form') as HTMLFormElement;
const tableBody_HTMLTableElement = document.getElementById('transactions-body') as HTMLTableElement;

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
    } catch (error) {
        console.error("Ошибка при отрисовке таблицы:", error);
    }
}

const inputSender_HTMLInputElement = document.getElementById('sender') as HTMLInputElement;
const inputReceiver_HTMLInputElement = document.getElementById('receiver') as HTMLInputElement;
const inputAmount_HTMLInputElement = document.getElementById('amount') as HTMLInputElement;

form_HMLFormElement.addEventListener('submit', async (e):Promise<void> => {
    e.preventDefault()
    try{
        await createTransaction(inputSender_HTMLInputElement.value, inputReceiver_HTMLInputElement.value, Number(inputAmount_HTMLInputElement.value))
        form_HMLFormElement.reset()
        await renderTable()
    } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }   
});

(window as any).handleDelete = async (id: number): Promise<void> => {
    if (confirm(`Вы действительно хотите удалить транзакцию N ${id}?`)){
        try {
            await deleteTransaction(id);
            await renderTable();
        } catch (error: any) {
        alert(`Error: ${error.message}`);
        throw error;
    }
    }
}

(window as any).handleEdit = async (id: number): Promise<void> => {
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
        } catch (error) {
            console.error("Ошибка при обновлении:", error);
        }
    }
}

renderTable()