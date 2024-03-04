import '../App.css';
import React from 'react';
import MaterialIcon, {colorPalette} from 'material-icons-react';



function StatusIcon(props) {

   const getIcon = (type, status) => {
      if (type == 'up-down') {
         if (status == 'up') {
            return (<MaterialIcon icon="arrow_upward" color={colorPalette.green._500} />)
         } else if (status == 'down') {
            return (<MaterialIcon icon="arrow_downward" color={colorPalette.red._500} />)
         }
      } else if (type == 'health') {
         if (status == 'healthy') {
            return (<MaterialIcon icon="check_circle" color={colorPalette.green._500} />)
         } else if (status == 'unhealthy') {
            return (<MaterialIcon icon="cancel" color={colorPalette.red._500} />)
         }
      }
   }

  return getIcon(props.type, props.status);
}
   
 
export default StatusIcon;

