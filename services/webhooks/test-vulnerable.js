const { exec } = require('child_process');

function exportEvents(req, res) {
  const partner = req.body.partner;

  exec(`/usr/local/bin/export-events --partner ${partner}`, (error, stdout) => {
    if (error) {
      return res.status(500).json({ error: 'export failed' });
    }

    res.json({ output: stdout });
  });
}

module.exports = { exportEvents };