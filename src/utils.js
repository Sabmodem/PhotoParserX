import axios from 'axios';

export const getConfig = async() => {
  try {
    const conf = await axios.get('/config');
    return conf.data;  
  } catch (err) {
    console.error(err);
    throw err;
  }
}

class StatusManager {
  constructor(statusModel) {
    this.text = statusModel.desctiption;
    switch (statusModel.position) {
      case 0:
        break
      case 1:
        break;
    }
  }
}