const generateKey = async () =>
    window.crypto.subtle.generateKey({
        name: 'AES-GCM',
        length: 256,
    }, true, ['encrypt', 'decrypt'])

const encode = data => {
    const encoder = new TextEncoder()

    return encoder.encode(data)
}

const generateIv = () =>
    window.crypto.getRandomValues(new Uint8Array(12))

const encrypt = async (data, key) => {
    const encoded = encode(data)
    const iv = generateIv()
    const cipher = await window.crypto.subtle.encrypt({
        name: 'AES-GCM',
        iv
    }, key, encoded)

    return {
        cipher,
        iv
    }
}

const pack = buffer => window.btoa(
    String.fromCharCode.apply(null, new Uint8Array(buffer))
)

const unpack = packed => {
    const string = window.atob(packed)
    const buffer = new ArrayBuffer(string.length)
    const bufferView = new Uint8Array(buffer)

    for (let i = 0; i < string.length; i++) {
        bufferView[i] = string.charCodeAt(i)
    }

    return buffer
}

const decode = byteStream => {
    const decoder = new TextDecoder()

    return decoder.decode(byteStream)
}

const decrypt = async (cipher, key, iv) => {
    const encoded = await window.crypto.subtle.decrypt({
        name: 'AES-GCM',
        iv
    }, key, cipher)

    return decode(encoded)
}

// поле для ввода сообщения, которое будет зашифровано
const input = document.querySelector('textarea')
// контейнер для вывода результатов
const output = document.querySelector('output')

// ключ
let key

const encryptAndSendMsg = async () => {
    const msg = input.value

     // шифрование
    key = await generateKey()

    const {
        cipher,
        iv
    } = await encrypt(msg, key)
    console.log(msg)
    console.log(cipher)
    decrypt_msg = decrypt(cipher, key, iv)
    console.log(decrypt_msg)
    // return cipher
    // упаковка и отправка

    url = 'http://127.0.0.1:8000/key_ssl'
    url+= '?client_partial=11111111111111' //+ pack(key)
    console.log(url)

    let response = await fetch(url, {

    });


    let text = await response.text(); // прочитать тело ответа как текст

    console.log(text)

    // await fetch('http://127.0.0.1:8000/create', {
    //     method: 'POST',
    //     body: JSON.stringify({
    //         text: pack(cipher),
    //         title: pack(iv)
    //     })
    // })
    //
    // output.innerHTML = `Сообщение <span>"${msg}"</span> зашифровано.<br>Данные отправлены на сервер.`
}

const getAndDecryptMsg = async () => {
    const res = await fetch('http://http://127.0.0.1:8000//create')

    const data = await res.json()

    // выводим данные в консоль
    console.log(data)

    // распаковка и расшифровка
    const msg = await decrypt(unpack(data.cipher), key, unpack(data.iv))

    output.innerHTML = `Данные от сервера получены.<br>Сообщение <span>"${msg}"</span> расшифровано.`
}

function myFunctionClient()   {
    document.getElementById('paragraph').innerHTML = "hello everyano"
}