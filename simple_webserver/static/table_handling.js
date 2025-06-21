// Javascript code that handles incoming measurement results, it makes a table
//with real time results.

const socket = io();

socket.on('new_data', (data) => {
  console.log("Received data through Socket.IO:", data); // Logging to console on incoming data

  const tbody = document.querySelector('#channel-table tbody');
  const rows = Array.from(tbody.rows);
  
  // Check if there's an existing row with the same transmitter & receiver
  const existingRow = rows.find(row =>
    row.cells[0].textContent === data.transmitter &&
    row.cells[1].textContent === data.receiver
  );

  if (existingRow) {
    existingRow.cells[2].textContent = data.timestamp;
    existingRow.cells[3].textContent = data.link_loss;
    existingRow.cells[4].textContent = data.delay;
    existingRow.cells[5].textContent = data.distance;
    existingRow.cells[6].textContent = data.quality;
  } else {
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
      <td>${data.transmitter}</td>
      <td>${data.receiver}</td>
      <td>${data.timestamp}</td>
      <td>${data.link_loss}</td>
      <td>${data.delay}</td>
      <td>${data.distance}</td>
      <td>${data.quality}</td>
    `;
    tbody.appendChild(newRow);
  }
});
