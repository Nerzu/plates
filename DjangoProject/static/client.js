
var base = 10

function rnd256() {
  const bytes = new Uint8Array(32);

  // load cryptographically random bytes into array
  window.crypto.getRandomValues(bytes);

  // convert byte array to hexademical representation
  const bytesHex = bytes.reduce((o, v) => o + ('00' + v.toString(16)).slice(-2), '');

  // convert hexademical value to a decimal string
  return BigInt('0x' + bytesHex).toString(10);
}


function bigPowMod(a, b, c) {
        // console.log("a:",typeof a,a)
        // console.log("b:",typeof b,b)
        // console.log("c:",typeof c,c)
        a = str2bigInt(a, base);
        b = str2bigInt(b, base);
        c = str2bigInt(c, base);
        // console.log("a:",typeof a,a)
        // console.log("b:",typeof b,b)
        // console.log("c:",typeof c,c)
        var result = powMod(a, b, c);
        result = bigInt2str(result, base);
        // console.log("result:",typeof result,result)
        return result;
      }

function power (a,n,p) {
    if (n === 0) {
        return 1
    } else {
        if (n % 2 === 0) {
            power((a * a) % p, n / 2, p)
        } else ((a * power(a, n - 1, p))) % p
    }
}

const generateKey = async () =>
    window.crypto.subtle.generateKey({
        name: 'AES-GCM',
        length: 256,
    }, true, ['encrypt', 'decrypt'])

const encode = data => {
    const encoder = new TextEncoder()

    return encoder.encode(data)
}

const decode = byteStream => {
    const decoder = new TextDecoder()

    return decoder.decode(byteStream)
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

function encrypt_msg (data, key) {
    var enc_msg = '';
    let str_msg = data;
    var i =0

    // console.log('type key:', typeof key)

    for(i=0; i<str_msg.length; i++){
        // console.log((str_msg[i].charCodeAt(0))+key)
        // console.log('type str_msg[i].charCodeAt(0):', typeof str_msg[i].charCodeAt(0))

        enc_msg+=String.fromCharCode((str_msg[i].charCodeAt(0))+key);
        // enc_msg+=String.fromCharCode((str_msg[i].charCodeAt(0))-key);
        // console.log(enc_msg);
    }
    // console.log("enc_data:", enc_msg.toString())
    return  enc_msg.toString()
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



const decrypt = async (cipher, key, iv) => {
    const encoded = await window.crypto.subtle.decrypt({
        name: 'AES-GCM',
        iv
    }, key, cipher)

    return decode(encoded)
}

// поле для ввода сообщения, которое будет зашифровано
const input_title = document.querySelector('input')
const input_text = document.querySelector('textarea')
// контейнер для вывода результатов
const output = document.querySelector('output')

// ключ
let key
var server_url = 'http://127.0.0.1:8000/key_ssl'


const encryptAndSendMsg = async () => {
    const title = input_title.value
    const msg = input_text.value

    url = server_url
    let response = await fetch(url);
    let text = await response.text();
    let response_json = JSON.parse(text)

    var key_p = response_json['p']
    var key_p_server = response_json['g']
    var key_server = response_json['A']
    var private_key_client = rnd256()
    var key_client = bigPowMod(key_p_server,private_key_client, key_p)
    var key_full = bigPowMod(key_server, private_key_client, key_p)

    key_enc = parseInt(key_full, 10)
    enc_msg =encrypt_msg(msg, key_enc)

    let response_two = await fetch(url,
        {
            method: 'POST',
        body: JSON.stringify({
            key_client: key_client,
            title: title,
            text: String(enc_msg),
            })
        });
    input_title.value = 'success'
    input_text.value = 'success'
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