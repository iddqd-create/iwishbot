
import React, { useState } from 'react';
import { Container, Box, Typography, TextField, Button, CircularProgress, IconButton } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import api from '../api';

const CreateWishlistScreen = ({ onBack, onWishlistCreated }) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreate = async () => {
    if (!name.trim()) {
      setError('Wishlist name is required.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/wishlists', { name });
      onWishlistCreated(response.data.id);
    } catch (err) {
      setError('Failed to create wishlist.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Create Wishlist
        </Typography>
      </Box>
      <TextField
        label="Wishlist Name"
        variant="outlined"
        fullWidth
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={!!error}
        helperText={error}
        sx={{ mb: 2 }}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={handleCreate}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} /> : 'Create'}
      </Button>
    </Container>
  );
};

export default CreateWishlistScreen;
