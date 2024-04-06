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
import {FormControl, Select, MenuItem} from '@mui/material';
import {Link, Accordion, AccordionSummary, AccordionDetails, Switch} from '@mui/material';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckIcon from '@mui/icons-material/Check';
import ChecklistIcon from '@mui/icons-material/Checklist';
import InfoIcon from '@mui/icons-material/Info';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import Brightness4Icon from '@mui/icons-material/Brightness4'; // Moon icon
import WbSunnyIcon from '@mui/icons-material/WbSunny'; // Sun icon
import './App.css';
import { createTheme, ThemeProvider } from '@mui/material/styles';

import Chat from './Chat.jsx'
import {drawerList} from './DrawerList.jsx'

const drawerWidth = 240;

// Define light mode theme
const lightTheme = createTheme({
    palette: {
        primary: {
            main: '#1D503B',
        },
        secondary: {
            main: '#82CEA0',
        },
        background: {
            default: '#f7fcf', // Background color
          },
          text: {
            primary: '#000000', // Primary text color
            secondary: '#757575', // Secondary text color
          },
    },
    typography: {
        fontFamily: 'Roboto, sans-serif', // Default font family
        
    },
    components: {
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: '#CAD9CA', // Background color for Accordion
          },
        },
      },
      MuiAccordion: {
        styleOverrides: {
          root: {
            backgroundColor: '#f7fcf', // Background color for Accordion
          },
        },
      },
      
      MuiAccordionDetails: {
        styleOverrides: {
          root: {
            backgroundColor: '#CAD9CA', // Background color for Accordion
          },
        },
      },
      MuiLink: {
        styleOverrides: {
          root: {
            color: '#000000', // Background color for Accordion
          },
        },
      },
    },
  });


// Define dark mode theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1D503B',
    },
  },
});

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

  const [darkMode, setDarkMode] = useState(false);
    
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

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  // Define the opacity for the icon
  const iconOpacity = 0.5;

  // Render Accordion for each category
  const renderAccordions = () => {
    return Object.keys(drawerList).map(category => (
      
      <Accordion key={category} disableGutters={true} style={{paddingLeft: '14px'}}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls={`${category}-content`}
          id={`${category}-header`}
          sx = {{ borderBottom:'1px solid black'}} 
          
        >
          <Typography variant='h7'>{category}</Typography>
        </AccordionSummary>
        <AccordionDetails  style={{overflowY: 'auto'}}>
            <List sx={{width: '100%'}} >
                {drawerList[category].map((item, index) => (
                  <ListItem key={index} sx={{pl: 1, padding:0}}>
                    <ListItemText >
                    <Link  href={item.url} color="primary">
                      
                        {item['display name']}
                      
                    </Link>
                    </ListItemText>
                  </ListItem>
                ))}
            </List>
        </AccordionDetails>
      </Accordion>
    ));
  };

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <Box sx={{ display: 'flex'}} >
        
        <CssBaseline />
        <AppBar position="fixed" open={open}>

            <Toolbar style={{justifyContent: 'space-between'}}>
            
            <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerOpen}
                edge="start"
                sx={{ mr: 2, ...(open && { color: 'transparent' }) }}
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
            
            <Switch 
                checked={darkMode} 
                onChange={toggleDarkMode} 
                icon={<WbSunnyIcon sx={{color: '#F3B262'}} />} // Sun icon for light mode
                checkedIcon={<Brightness4Icon />} // Moon icon for dark mode
                sx={{
                    '& .MuiSwitch-track': {
                        backgroundColor: darkMode ? '#424242' : '#FDE9AE',
                        opacity: 1,
                    }
                }}
            />
            
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
            <DrawerHeader style={{justifyContent:'space-between',marginLeft:'20px'}}>
              
            <Typography variant="h6" noWrap component="div">Resources</Typography>
            <IconButton onClick={handleDrawerClose}>
                {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            </IconButton>
            </DrawerHeader>
            <Divider />
            <Box >
            {renderAccordions()}
            </Box>
        </Drawer>
        <Main open={open}>
            <DrawerHeader />
            <Chat />
        </Main>
        </Box>
    </ThemeProvider>
  );
}
