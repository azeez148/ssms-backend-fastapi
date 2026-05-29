import React from 'react';
import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import { WhatsAppFloatingButton } from '../common';
import { config } from '../../config';

const Layout: React.FC = () => {
  const whatsappNumber = config.whatsappNumber;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Outlet />
      </Box>
      <Footer />
      <WhatsAppFloatingButton phoneNumber={whatsappNumber} />
    </Box>
  );
};

export default Layout;
