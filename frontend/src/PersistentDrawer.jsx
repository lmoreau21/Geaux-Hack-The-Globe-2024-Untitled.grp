import React, {useState} from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import CssBaseline from '@mui/material/CssBaseline';
import MuiAppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MedicalInformationIcon from '@mui/icons-material/MedicalInformation';
import CheckIcon from '@mui/icons-material/Check';
import ChecklistIcon from '@mui/icons-material/Checklist';
import InfoIcon from '@mui/icons-material/Info';

import Chat from './Chat.jsx'
import {drawerList} from './DrawerList.jsx'

const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: `-${drawerWidth}px`,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    }),
  }),
);

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export let data_choice = 'la_medicaid';

export function getDataChoice() {
    return data_choice;
}




export default function PersistentDrawer() {
  const theme = useTheme();
  const [dataChoice, setDataChoice] = useState(getDataChoice());

  const [open, setOpen] = React.useState(false);

    
  const handleChange = (event) => {
    data_choice = event.target.value;
    setDataChoice(data_choice);
  };
  
  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  // Render dropdown menu for each category
  const renderDropdowns = () => {
    return Object.keys(drawerList).map(category => (
      <div key={category}>
        <h3>{category}</h3>
        <select>
          {drawerList[category].map((item, index) => (
            <option key={index} value={item.url}>{item['display name']}</option>
          ))}
        </select>
      </div>
    ));
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <FormControl  variant="standard" focused>
            
            <Select
              labelId="data-select-label"
              id="data-select"
              value={dataChoice}
              
              label="Data"
              style={{color: 'white'}}
              onChange={handleChange}
            >
              <MenuItem value={"la_medicaid"}><Typography variant="h6" noWrap component="div">LA Medicaid Chatbot</Typography></MenuItem>
              <MenuItem value={'gov_medicare'}><Typography variant="h6" noWrap component="div">Gov Medicare Chatbot</Typography></MenuItem>
              <MenuItem value={'insurance'}> <Typography variant="h6" noWrap component="div"> Insurance Chatbot</Typography></MenuItem>
            </Select>
          </FormControl>
         
        </Toolbar>
        
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="persistent"
        anchor="left"
        open={open}
      >
        <DrawerHeader>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </DrawerHeader>
        <Divider />
        <List>
          {renderDropdowns()}
        </List>
      </Drawer>
      <Main open={open}>
        <DrawerHeader />
        <Chat />
      </Main>
    </Box>
  );
}
