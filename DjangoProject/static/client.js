
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
        console.log("a:",typeof a,a)
        console.log("b:",typeof b,b)
        console.log("c:",typeof c,c)
        a = str2bigInt(a, base);
        b = str2bigInt(b, base);
        c = str2bigInt(c, base);
        console.log("a:",typeof a,a)
        console.log("b:",typeof b,b)
        console.log("c:",typeof c,c)
        var result = powMod(a, b, c);
        result = bigInt2str(result, base);
        console.log("result:",typeof result,result)
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
const input_title = document.querySelector('input')
const input_text = document.querySelector('textarea')
// контейнер для вывода результатов
const output = document.querySelector('output')

// ключ
let key

const encryptAndSendMsg = async () => {
    const title = input_title.value
    const msg = input_text.value

    // шифрование
    // key = await generateKey()

    url = 'http://127.0.0.1:8000/key_ssl'
    // url+= '?client_partial=11111111111111' //+ pack(key)
    console.log(url)

    let response = await fetch(url);
    let text = await response.text(); // прочитать тело ответа как текст
    console.log(text)
    let response_json = JSON.parse(text)

    // var key_s = parseInt(response_json['session_key'], 10)
    // var key_p = parseInt(response_json['p'], 10)
    // var key_p_server = parseInt(response_json['g'], 10)
    // var key_server = parseInt(response_json['A'], 10)
    var key_s = response_json['session_key']
    var key_p = response_json['p']
    var key_p_server = response_json['g']
    var key_server = response_json['A']
    console.log("key_session:", typeof key_s,key_s)
    console.log("key_public:", typeof key_p, key_p)
    console.log("key_server:", typeof key_server, key_server)

    // var private_key_client = '57864519447101809354481595270012471035729382219440199100252543963896390963236'
    var private_key_client = rnd256()
    // console.log('test_2256:', typeof test_256, test_256)


    console.log("private_key_client:", typeof private_key_client, private_key_client)

    var key_client = bigPowMod(key_p_server,private_key_client, key_p)
    console.log("key_client:",key_client)

    console.log("title:",title)
    console.log("text:",msg)

    var key_full = bigPowMod(key_server, private_key_client, key_p)
    console.log("key_full:",key_full)

    let response_two = await fetch(url,
        {
            method: 'POST',
        body: JSON.stringify({
            key_client: key_client,
            key_full: key_full,
            title: title,
            text: msg
            })
        });

    input_title.value = 'success'
    input_text.value = 'success'

    // let text_two = await response.text(); // прочитать тело ответа как текст
    // console.log(text)
    // let response_json_two = JSON.parse(text_two)

    // const {
    //     cipher,
    //     iv
    // } = await encrypt(msg, key_s)
    // console.log(msg)
    // console.log(cipher)
    // decrypt_msg = decrypt(cipher, key, iv)
    // console.log(decrypt_msg)
    //
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