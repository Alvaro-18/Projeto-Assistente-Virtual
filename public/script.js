const recordButton = document.querySelector("button");
let mediaRecorder;
let audioChunks = [];
let columns = []
let error = ""
const btnLeft = document.getElementById("left");
const btnRight =  document.getElementById("right")

  // Função para converter o Blob de áudio para o formato WAV
async function convertToWav(blob) {
  const arrayBuffer = await blob.arrayBuffer();
  const audioContext = new AudioContext();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  const wavData = audioBufferToWav(audioBuffer);
  const wavBlob = new Blob([new DataView(wavData)], { type: "audio/wav" });

  return wavBlob;
}

// Função para converter AudioBuffer para WAV
function audioBufferToWav(audioBuffer) {
  const numOfChannels = audioBuffer.numberOfChannels;
  const length = audioBuffer.length * numOfChannels * 2 + 44;
  const buffer = new ArrayBuffer(length);
  const view = new DataView(buffer);

  // Header do arquivo WAV
  writeString(view, 0, "RIFF");
  view.setUint32(4, length - 8, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // fmt chunk size
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, numOfChannels, true);
  view.setUint32(24, audioBuffer.sampleRate, true);
  view.setUint32(28, audioBuffer.sampleRate * numOfChannels * 2, true);
  view.setUint16(32, numOfChannels * 2, true); // block align
  view.setUint16(34, 16, true); // bits per sample
  writeString(view, 36, "data");
  view.setUint32(40, audioBuffer.length * numOfChannels * 2, true);

  // Dados de áudio
  const channelData = [];
  for (let i = 0; i < numOfChannels; i++) {
    channelData.push(audioBuffer.getChannelData(i));
  }

  let offset = 44;
  for (let i = 0; i < audioBuffer.length; i++) {
    for (let channel = 0; channel < numOfChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, channelData[channel][i]));
      view.setInt16(offset, sample * 0x7fff, true);
      offset += 2;
    }
  }

  return buffer;
}

// Função para escrever strings no DataView
function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}


recordButton.addEventListener("click", async () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      recordButton.classList.remove("recording");
      // Converte os dados de áudio em um Blob e envia para o backend
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const wavBlob = await convertToWav(audioBlob)

      const formData = new FormData();
      formData.append("audio", wavBlob);

      // Envia o áudio para o backend Flask
      try {
        const response = await fetch("reconhecer_comando", {
          method: "POST",
          body: formData
        });
      
        const result = await response.json();  
        if (response.ok) {
          alert(result.message);
          renderColumns();  
        } else {
          alert("Erro no servidor: " + result.message);  
        }
      } catch (error) {
        mediaRecorder.stop();
        console.error("Erro:", error);
      }

      audioChunks = [];
    };

    mediaRecorder.start();
    recordButton.classList.add("recording");
  } else {
    mediaRecorder.stop();
    recordButton.classList.remove("recording");
  }
});

btnLeft.addEventListener("click", () => {
  document.getElementById("scroll-container").scrollBy({
    left: -150,
    behavior: "smooth"
  });
});

btnRight.addEventListener("click", () => {
  document.getElementById("scroll-container").scrollBy({
    left: 150,
    behavior: "smooth"
  });
});

async function renderColumns() {
  const container = document.getElementById("scroll-container");
  container.innerHTML = "";

  try {
    const response = await fetch("pegar_dados", {
      method: "GET"
    })

    if (!response.ok) {
      throw new Error('Erro ao pegar os dados');
    }

    const data = await response.json()

    const groupedData = data.dados.reduce((acc, atividade) => {
      if (!acc[atividade.date]) {
        acc[atividade.date] = [];
      }
      acc[atividade.date].push(atividade);
      return acc;
    }, {});
  
    if(Object.keys(groupedData).length >= 3) {
      btnLeft.style.display = "flex";
      btnRight.style.display = "flex";
    }
  
    Object.keys(groupedData).forEach(date => {
      const column = document.createElement("div");
      column.classList.add("column");
  
      const head = document.createElement("div");
      head.classList.add("head");
  
      const dateElement = document.createElement("p");
      dateElement.textContent = date;
      head.appendChild(dateElement);
  
      const total = document.createElement("p");
      total.textContent = `Total: ${groupedData[date].length}`;
      head.appendChild(total);
  
      column.appendChild(head);
  
  
      groupedData[date].forEach(cardData => {
        const card = document.createElement("div");
        cardData.status
          ? card.classList.add("cardClosed")
          : card.classList.add("card");
  
        const text = document.createElement("p");
        text.id = "text";
        text.textContent = cardData.text;
        card.appendChild(text);
  
        const status = document.createElement("p");
        status.classList.add("status");
        status.innerHTML = `Status: <span>${cardData.status ? "Fechado" : "Aberto"}</span>`;
        card.appendChild(status);
  
        column.appendChild(card);
      });
  
      container.appendChild(column);
    });
  } catch (error) {
    console.log("Erro renderizando o board", error)
  }
}

renderColumns();
