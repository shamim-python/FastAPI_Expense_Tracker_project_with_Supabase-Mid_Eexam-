from test.test_main import client
from fastapi import status
from main import app
from router.auth import get_current_user
from database import sessionlocal
from models import Transactions



def override_get_current_user():
    return{
        'id':5,
        'username':'test_user'
    }
app.dependency_overrides[get_current_user]=override_get_current_user
def test_read_transaction():
    response=client.get('/')
    assert response.status_code==200

def test_read_specifique_transaction():
    response = client.get('/transaction/2/')
    
    print(response.status_code)
    print(response.json())
    
    assert response.status_code == status.HTTP_200_OK
def test_creat_transaction():
    db = sessionlocal()

    # db.query(Transactions).filter(Transactions.id == 3).delete()
    # db.commit()

    request_data = {
        'title': 'masha_allah',
        'amount': 3000,
        'type': 'income',
        'category': 'str',
        'date': '2026-09-28'
    }

    response = client.post('/creat/', json=request_data)

    assert response.status_code == status.HTTP_200_OK

    db.close()

def test_updat_transaction():


    request_update={    
    'title': 'kichekta',
    'amount': '1300',
    'type': 'income',
    'category': 'adada'
    }
    response=client.put('/update/1',json=request_update)
    assert response.status_code==status.HTTP_200_OK

def test_delete_transaction():
    response=client.delete('/delete_transactions/3')
    response.status_code=status.HTTP_200_OK      