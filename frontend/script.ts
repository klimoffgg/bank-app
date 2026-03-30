const API_URL = 'http://localhost:8000';

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

 