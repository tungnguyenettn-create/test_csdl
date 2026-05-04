
-- Create new branchs syntax 
CALL create_branch(
    'Ha Noi',
    'BIDV Ha Noi'
); 

CALL create_branch(
    'Phu Tho',
    'BIDV Vinh Phuc'
); 


CALL create_employee(
    2, 
    'Duong Phan Quang Bach', 
    '001206031', 
    'b@chl0v9ic9cre@m'
); 

CALL create_employee(
    1,
    'Nguyen Duc Tung',
    '001206032',
    't0ngis@v0iddr9am9rs' 
); 

CALL create_customer(
    'Nguyen Dac Hai Dang', 
    '001206033',
    'Vietnamese',
    '2006-10-10',
    'Ha Noi',
    '13-Ha Loi',
    1
);

CALL create_customer(
    'Nguyen Doan Hong Thai', 
    '001206035', 
    'Vietnamese',
    '2006-10-10',
    'Ha Noi',
    '13-Ha Loi',
    1
);

-- Tao account bang cccd cho de nhe :)))
CALL create_account(
    '0012060350',
    2 , --anh Thai
    'thai', 
    1 ,--bach 
    1000000
);

-- Tao account bang cccd cho de nhe :)))
CALL create_account(
    '0012060351',
    2 , --anh Thai
    'thai', 
    2 ,--tung 
    500000
);

-- Tao account bang cccd cho de nhe :)))
CALL create_account(
    '0012060330',
    1 , --anh Dang
    'dang', 
    2 ,--tung 
    0
);

CALL in_bank_transfer(
    '0012060351', --hien dang co 500000
    '0012060330',  --hien dang co 0
    250000,
    'Tang anh Dang sinh nhat'
);
--0012060351 se co 250000 
--0012060330 se co 250000

CALL out_bank_transfer(
    '0012060351', --hien dang co 250000
    50000,
    'Tien an sang', 
    'BIDV',  --ngan hang nao day
    '123456' --id nao day
);
--0012060351 se con 200000 

CALL pay_bill(
    '0012060350', --hien dang co 1000000
    500000,
    'Chau chuyen tien nha a', 
    'Accomodation Bills'
); 
--0012060350 se con 500000 

CALL withdraw_cash(
    '0012060330',
    1, --bach se giup dang withdraw
    100000,
    'Lay tien ve que an tet'
);

-- 0012060330 se con 150000

CALL deposit_cash(
    '0012060330',
    1, --bach se giup dang withdraw
    200000,
    'Tien di lam them'
);
-- 0012060330 se them 350000 

SELECT * FROM branch;
SELECT * FROM employee;  
SELECT * FROM customer; 
SELECT * FROM account;
