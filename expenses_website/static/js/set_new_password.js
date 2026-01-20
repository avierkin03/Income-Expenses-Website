const passwordField = document.querySelector('#passwordField');
const passwordField2 = document.querySelector('#passwordField2');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const showPasswordToggle2 = document.querySelector('.showPasswordToggle2');

const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent === 'SHOW'){
        showPasswordToggle.textContent = 'HIDE';
        passwordField.setAttribute('type', 'text');
    } else {
        showPasswordToggle.textContent = 'SHOW';
        passwordField.setAttribute('type', 'password');
    }
};

const handleToggleInput2 = (e) => {
    if (showPasswordToggle2.textContent === 'SHOW'){
        showPasswordToggle2.textContent = 'HIDE';
        passwordField2.setAttribute('type', 'text');
    } else {
        showPasswordToggle2.textContent = 'SHOW';
        passwordField2.setAttribute('type', 'password');
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);
showPasswordToggle2.addEventListener('click', handleToggleInput2);