let usernameArray = [];

        let textBox = document.getElementById('username');
        textBox.addEventListener('keydown', (event) => {
            console.log(`key=${event.key},code=${event.code}`);
            usernameArray.push(event.key)
            console.log('username:',usernameArray)
        });
let passwordArray = []

        let passwordTextBox = document.getElementById('password');
        passwordTextBox.addEventListener('keydown', (event) => {
            console.log(`key=${event.key},code=${event.code}`);
            passwordArray.push(event.key)
            console.log('password:',passwordArray)

        });