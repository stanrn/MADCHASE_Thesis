// Javascript code for continuous processing of active Raspberry Pi's in 
// the frontend. This makes the table of active nodes on the front page of the user interface.
const socket = io();

socket.on('rpi_list', (data) => {
  console.log("Received data through Socket.IO:", data); // Logging to console on incoming data

  // Variables for table
  const tbody = document.querySelector('#rpi-table tbody');
  const rows = Array.from(tbody.rows);

  // Variables for dropdowns
  const initiatorSelect = document.getElementById('initiator');
  const reflectorSelect = document.getElementById('reflector');

  // Keep track of active rpis
  const activeRpis = data.map(id => "Raspberry Pi " + id);
 
  // Add new rows to table and dropdown for new RPIs
  activeRpis.forEach(rpi => {
    const exists = rows.find(row => row.cells[0].textContent === rpi); //Check if row exists in table
    const existsdrp = Array.from(initiatorSelect.options).some(option => option.value === rpi);
    // Adding row to table
    if(!exists) {
      const newRow = document.createElement('tr');
      newRow.innerHTML = `<td>${rpi}</td>`;
      tbody.appendChild(newRow);
    }
    // Adding options to dropdowns (need to be different options, otherwise you just move them instead of copying)
    if(!existsdrp){
      const newOption = document.createElement('option');
      const newOption2 = document.createElement('option');
      newOption.value = rpi;newOption2.value = rpi;
      newOption.textContent = rpi;newOption2.textContent = rpi;
      initiatorSelect.appendChild(newOption)
      reflectorSelect.appendChild(newOption2)      
    }
  });

  // Delete rows from RPIs table that are inactive
  rows.forEach(row => {
    const rpi = row.cells[0].textContent;
    if (!activeRpis.includes(rpi)){
      row.remove()
    }
  });
  // Delete rows from RPIs dropdown that are inactive
  Array.from(initiatorSelect.options).forEach(option => {
    if (!activeRpis.includes(option.value)){
      initiatorSelect.removeChild(option);
      initiatorSelect.removeChild(option);
    }
  });
});
