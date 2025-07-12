const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({ origin: '*', credentials: true }));
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Backend is running!' });
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Backend running on port ${port}`)); 