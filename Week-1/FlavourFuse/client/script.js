import bot from './assets/chef.svg'
import user from './assets/user.svg'

const form = document.querySelector('form')
const chatContainer = document.querySelector('#chat_container')

let loadInterval

function loader(element) {
    element.textContent = ''

    loadInterval = setInterval(() => {
        // Update the text content of the loading indicator
        element.textContent += '.';

        // If the loading indicator has reached three dots, reset it
        if (element.textContent === '....') {
            element.textContent = '';
        }
    }, 300);
}

function typeText(element, text) {
    let index = 0

    let interval = setInterval(() => {
        if (index < text.length) {
            element.innerHTML += text.charAt(index)
            index++
        } else {
            clearInterval(interval)
        }
    }, 20)
}

// generate unique ID for each message div of bot
// necessary for typing text effect for that specific reply
// without unique ID, typing text will work on every element
function generateUniqueId() {
    const timestamp = Date.now();
    const randomNumber = Math.random();
    const hexadecimalString = randomNumber.toString(16);

    return `id-${timestamp}-${hexadecimalString}`;
}

function chatStripe(isAi, value, uniqueId) {
    return (
        `
        <div class="wrapper ${isAi && 'ai'}">
            <div class="chat">
                <div class="profile">
                    <img 
                      src=${isAi ? bot : user} 
                      alt="${isAi ? 'bot' : 'user'}" 
                    />
                </div>
                <div class="message" id=${uniqueId}>${value}</div>
            </div>
        </div>
    `
    )
}
var languageCode = 'en';
var languageText = 'English';

function loadLanguages() {
    fetch('languages.json') // must be in public folder acc. to Vite
        .then(response => response.json())
        .then(data => {
            const dropdown = document.querySelector('.dropdown-content');
            data.languages.forEach(language => {
                // Instead of creating an anchor tag, we are creating an 'option'
                // element since we want a dropdown list.
                const option = document.createElement('option');
                option.text = language.lang
                option.value = language.code
                dropdown.appendChild(option);

                if (language.code === 'en') {
                    option.classList.add('selected'); // Set the 'selected' class for the default language
                }
            });
            languageCode = 'en'; // Set the default language code
            languageText = 'English';
            
            dropdown.addEventListener('change', () => {
                const selectedOption = dropdown.options[dropdown.selectedIndex];
                
                languageCode = selectedOption.value
                languageText = selectedOption.text
            });
        })
        .catch(error => console.error(error));


    // Add event listener to the dropbtn button
    // const dropbtn = document.querySelector('.dropbtn');
    // dropbtn.addEventListener('click', () => {
    //     const dropdownContent = document.querySelector('.dropdown-content');
    //     dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    // });
}


window.addEventListener('load', loadLanguages);


const handleSubmit = async (e) => {
    e.preventDefault()

    const data = new FormData(form)

    // user's chatstripe
    chatContainer.innerHTML += chatStripe(false, data.get('prompt'))

    // to clear the textarea input 
    form.reset()

    // bot's chatstripe
    const uniqueId = generateUniqueId()
    chatContainer.innerHTML += chatStripe(true, " ", uniqueId)

    // to focus scroll to the bottom 
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // specific message div 
    const messageDiv = document.getElementById(uniqueId)

    // messageDiv.innerHTML = "..."
    loader(messageDiv)

    const response = await fetch('https://mrecipes.onrender.com/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: data.get('prompt'),
            langcode: languageCode,
            langtext: languageText
        })
    })

    clearInterval(loadInterval)
    messageDiv.innerHTML = " "

    if (response.ok) {
        const data = await response.json();
        console.log(data)
        console.log(data.bot)
        const parsedData = data.bot.trim() // trims any trailing spaces/'\n' 
        console.log(parsedData)
        typeText(messageDiv, parsedData)
    } else {
        const err = await response.text()

        messageDiv.innerHTML = "Something went wrong"
        alert(err)
    }
}

form.addEventListener('submit', handleSubmit)
form.addEventListener('keyup', (e) => {
    if (e.keyCode === 13) {
        handleSubmit(e)
    }
})