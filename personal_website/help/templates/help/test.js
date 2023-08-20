var receiveBuffer = []; // 存放数据的数组
var receiveSize = 0; // 数据大小
onmessage = (event) => {   // 每次事件被触发时，说明有数据来了，将收到的数据放到数组中  
    receiveBuffer.push(event.data);  // 更新已经收到的数据的长度  
    receivedSize += event.data.byteLength;   // 如果接收到的字节数与文件大小相同，则创建文件  
    if (receivedSize === fileSize) { //fileSize 是通过信令传过来的
        // 创建文件    
        var received = new Blob(receiveBuffer, {type: 'application/octet-stream'});    
        // 将 buffer 和 size 清空，为下一次传文件做准备    
        receiveBuffer = [];    
        receiveSize = 0;        // 生成下载地址    
        downloadAnchor.href = URL.createObjectURL(received);    
        downloadAnchor.download = fileName;    
        downloadAnchor.textContent = `Click to download '${fileName}' (${fileSize} bytes)`;    
        downloadAnchor.style.display = 'block';  }
    }

function sendData() {   
    var offset = 0; // 偏移量  
    var chunkSize = 16384; // 每次传输的块大小  
    var file = fileInput.files[0]; // 要传输的文件，它是通过 HTML 中的 file 获取的  ...   // 创建 fileReader 来读取文件  
    fileReader = new FileReader();  
    fileReader.onload = e => { // 当数据被加载时触发该事件
        dc.send(e.target.result); // 发送数据    
        offset += e.target.result.byteLength; // 更改已读数据的偏移量
        if (offset < file.size) { // 如果文件没有被读完      
            readSlice(offset); // 读取数据    
        }  
    }   
    var readSlice = o => {    
        const slice = file.slice(offset, o + chunkSize); // 计算数据位置    
        fileReader.readAsArrayBuffer(slice); // 读取 16K 数据  
    };   
    readSlice(0); // 开始读取数据 
}

// 获取文件相关的信息
fileName = file.name;
fileSize = file.size;
fileType = file.type;
lastModifyTime = file.lastModified; // 向信令服务器发送消息
sendMessage(roomid,   {    // 将文件信息以 JSON 格式发磅   
    type: 'fileinfo',    
    name: file.name,    
    size: file.size,    
    filetype: file.type,    
    lastmodify: file.lastModified  
});

socket.on('message', (roomid, data) => {   // 如果是 fileinfo 类型的消息  
    if(data.hasOwnProperty('type') && data.type === 'fileinfo'){    // 读出文件的基本信息    
        fileName = data.name;    
        fileType = data.filetype;    
        fileSize = data.size;    
        lastModifyTime = data.lastModify; 
    }
})