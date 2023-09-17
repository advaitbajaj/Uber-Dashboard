window.myNamespace = Object.assign({}, window.myNamespace, {  
    mySubNamespace: {  
        pointToLayer: function (feature, latlng, context) {
            const greenIcon = L.icon({
                iconUrl: 'assets\\images\\placeholder.png',
                // shadowUrl: 'https://leafletjs.com/examples/custom-icons/leaf-shadow.png',
                iconSize: [30, 30], // size of the icon
                // shadowSize: [50, 64], // size of the shadow
                // iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
                // shadowAnchor: [4, 62],  // the same for the shadow
                // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            });
            return L.marker(latlng, {icon: greenIcon})  
        }  
    }
});