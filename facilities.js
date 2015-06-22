window.l = [];
var facilityTree = function(nlat, wlng, slat, elng) {
    // Ajax request made below node definition
    var self = this;
    this.nlat = nlat;
    this.wlng = wlng;
    this.slat = slat;
    this.elng = elng;

    var facilityNode = function(obj) {
        
        // Bounding Box
        this.en = obj.en;
        this.ws = obj.ws;

        this.center = obj.center;
        this.sep = obj.sep;

        // Stats
        this.uncompressedSize = obj.uncompressedSize || 0;
        this.compressedSize = obj.compressedSize || 0;
        this.count = obj.count || 0;

        // Data
        this.isRoot = obj.isRoot
        this.isLeaf = obj.isLeaf
        this.children = {};
        if (this.isLeaf) {
            this.setFacilities(obj.data);
            drawBox(this.en, this.ws, "#FF0000", obj);
        } else {
            drawBox(this.en, this.ws, "#0000FF");
        }

        // Children
        if (obj.children) {
            if (obj.children.wn)
                this.children.wn = new facilityNode(obj.children.wn);
            if (obj.children.en)
                this.children.en = new facilityNode(obj.children.en);
            if (obj.children.ws)
                this.children.ws = new facilityNode(obj.children.ws);
            if (obj.children.es)
                this.children.es = new facilityNode(obj.children.es);
        }
    
    };

    facilityNode.prototype.print = function(indent) {
        var indent = indent || "";
        var shift = "--";
    
        console.log(indent + " Node: " + this.center[1], this.center[0], this.count);
        if (this.children.wn && this.children.wn.count) { 
            console.log(indent + shift + " NW");
            this.children.wn.print(indent + shift)
        }
    
        if (this.children.en && this.children.en.count) { 
            console.log(indent + shift + " NE");
            this.children.en.print(indent + shift)
        }
    
        if (this.children.ws && this.children.ws.count) { 
            console.log(indent + shift + " SW");
            this.children.ws.print(indent + shift)
        }
    
        if (this.children.es && this.children.es.count)  {
            console.log(indent + shift + " SE");
            this.children.es.print(indent + shift)
        }
    
        console.log(indent + "__");
    };
    
    facilityNode.prototype.setFacilities = function(facilities) {
        var id = this.en[1]+""+this.ws[0]+""+this.ws[1]+""+this.en[0];
        localStorage.setItem(id, facilities);
    };
    
    facilityNode.prototype.getFacilities = function() {
        var id = this.en[1]+""+this.ws[0]+""+this.ws[1]+""+this.en[0];
        return JSON.parse(LZString.decompressFromUTF16(localStorage[id]));
    };

    facilityNode.prototype.within = function(lat, lng) {
        var self = this;
        return ((lat < self.en[1] && lat >= self.ws[1]) 
               && (lng > self.ws[0] && lng <= self.es[0]));
    }

    facilityNode.prototype.crossesBound = function(nlat, wlng, slat, elng) {
        var self = this;

        if ((nlat < self.ws[1]) || (slat > self.en[1]))
            return false;
        
        if ((wlng > self.en[0]) || (elng < self.ws[0])) 
           return false;
        
        return true;
    }

    facilityNode.prototype.distance = function(lat, lng) {
        var self = this;
        var R = 6371000; // metres
        var e = self.center[1] * Math.PI/180;
        var f = lat * Math.PI/180;
        var g = (lat - self.center[1]) * Math.PI/180;
        var h = (lng - self.center[0]) * Math.PI/180;

        var a = Math.sin(g/2) * Math.sin(g/2) +
                Math.cos(e) * Math.cos(f) *
                Math.sin(h/2) * Math.sin(h/2);

        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c;
    }

    // Revisit ajax req
    $.ajax({
        url: "http://localhost:3000/api/v0/facilities.json",
        data: {
            within: self.nlat + "," + self.wlng + "," + self.slat + "," + self.elng,
            compressed: 'anything can be here',
            //fields: "name,uuid,coordinates,properties:sector", 
        },
        success: function(data) {
            console.log("Recieved Data traversing");
            self.total = data.total;
            self.root = new facilityNode(data.facilities); 
        },
        error: function(data) {
            console.log("Done");
        },
    });

    console.log("http://localhost:3000/api/v0/facilities.json", "?within=", 
            self.nlat + "," + self.wlng + "," + self.slat + "," + self.elng, 
            "&compressed");

}

facilityTree.prototype._getNNode = function(lat, lng, node) {
    var self = this;

    // Maybe I'm a leaf?
    if (node.isLeaf) { 
        return node;
    }

    if (node.count > 0) {
        // NW
        if (node.children.wn && node.children.wn.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.children.wn);
            if (cnode) 
                return cnode;
        }

        // NE
        if (node.children.en && node.children.en.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.children.en);
            if (cnode) 
                return cnode;
        }

        // SW
        if (node.children.ws && node.children.ws.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.children.ws);
            if (cnode) 
                return cnode;
        }

        // SE
        if (node.children.es && node.children.es.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.children.es);
            if (cnode) 
                return cnode;
        }
    }
}

facilityTree.prototype.getNNode = function(lat, lng) {
    var self = this;

    if (!self.root.within(lat, lng))
        return null;

    var node = self._getNNode(lat, lng, self.root);
    console.log('node: ', node.center[1], node.center[0], "distance from center", node.distance(lat,lng));

    return node;
}

facilityTree.prototype._getRNodes = function(nlat, wlng, slat, elng, node) {
    var self = this;

    // Maybe I'm a leaf?
    if (node.isLeaf) { 
        return [node]
    }

    var nodes = [];
    if (node.count > 0) {
        // NW
        if (node.children.wn && node.children.wn.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.children.wn));
        }

        // NE
        if (node.children.en && node.children.en.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.children.en));
        }

        // SW
        if (node.children.ws && node.children.ws.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.children.ws));
        }

        // SE
        if (node.children.es && node.children.es.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.children.es));
        }
    }

    return nodes;
}

facilityTree.prototype.getRNodesBox = function(nlat, wlng, slat, elng) {
    var self = this;

    if (!self.root.crossesBound(nlat, wlng, slat, elng))
        return null;

    var nodes = self._getRNodes(nlat, wlng, slat, elng, self.root);
    return nodes;
}

facilityTree.prototype.getRNodesRad = function(lat, lng, r) {
    var self = this;

    var R = 6378137;
    var dlat = r/R;
    var dlng = r/(R*Math.cos(Math.PI*lat/180));
    
    nlat = lat + dlat * 180/Math.PI;
    wlng = lng - dlng * 180/Math.PI;
    slat = lat - dlat * 180/Math.PI;
    elng = lng + dlng * 180/Math.PI;

    if (!self.root.crossesBound(nlat, wlng, slat, elng))
        return null;

    var nodes = self._getRNodes(nlat, wlng, slat, elng, self.root);
    return nodes;
     
}

facilityTree.prototype.getNNearestFacilities = function(lat, lng, r, n) {
    var self = this;

    // Calculates meter distance between facilities and center of node
    function dist(coordinates, clat, clng) {
       var lat = coordinates[1];
       var lng = coordinates[0];
    
       var R = 6371000;
       var e = clat * Math.PI/180;
       var f = lat * Math.PI/180;
       var g = (lat - clat) * Math.PI/180;
       var h = (lng - clng) * Math.PI/180;
    
       var a = Math.sin(g/2) * Math.sin(g/2) +
               Math.cos(e) * Math.cos(f) *
               Math.sin(h/2) * Math.sin(h/2);
    
       var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
       return R * c;
    }

    // Sort X Nodes Data
    var nodes = self.getRNodesRad(lat, lng, r);
    var nodeFacilities = [];
    nodes.forEach(function(node, idx) {
        var facilities = node.getFacilities();
        facilities.sort(function (facilityA, facilityB) {
            var lengthA = dist(facilityA.coordinates, lat, lng);
            var lengthB = dist(facilityB.coordinates, lat, lng);
            return (lengthA - lengthB); 
        });
        nodeFacilities.push(facilities);
    });

    //Merge X Nodes Sorted Data
    var facilities = [];
    while(n > 0 && nodeFacilities.length > 0) {
        nodeFacilities = nodeFacilities.filter(function(facilities) {
            return facilities.length;
        });

        var tops = [];
        nodeFacilities.forEach(function(facilities, idx) {
            tops.push({'fac': facilities[0], 'idx': idx});
        }); 

        tops.sort(function (nodeA, nodeB) {
            var lengthA = dist(nodeA.fac.coordinates, lat, lng);
            var lengthB = dist(nodeB.fac.coordinates, lat, lng);
            return (lengthA - lengthB); 
        });

        //XXX: Should terminate early if this is the case instead 
        if (tops.length > 0) 
            facilities.push(nodeFacilities[tops[0].idx].shift());

        n--;
    }

    return facilities;
}

facilityTree.prototype.print = function() {
    this.root.print();
}

facilityTree.prototype._getLeaves = function(node) {
    var self = this;

    // Check if this is a leaf
    if (node.isLeaf) 
        return [node];

    // Otherwise check all children
    var nodes = [];
    if (node.count > 0) {
        // NW
        if (node.children.wn) 
            nodes = nodes.concat(self._getLeaves(node.children.wn));

        // NE
        if (node.children.en) 
            nodes = nodes.concat(self._getLeaves(node.children.en));

        // SW
        if (node.children.ws) 
            nodes = nodes.concat(self._getLeaves(node.children.ws));

        // SE
        if (node.children.es) 
            nodes = nodes.concat(self._getLeaves(node.children.es));
    }

    return nodes;
}

facilityTree.prototype.getLeaves = function() {
    var self = this;
    return self._getLeaves(self.root);
}

facilityTree.prototype.getCompressedSize = function() {
    var self = this;
    var leaves = self._getLeaves(self.root);;
    return leaves.reduce(function(sum, node) {
        return node.compressedSize + sum;
    }, 0);
};

facilityTree.prototype.getUncompressedSize = function() {
    var self = this;
    var leaves = self._getLeaves(self.root);
    return leaves.reduce(function(sum, node) {
        return node.uncompressedSize + sum;
    }, 0);
};

facilityTree.prototype.getCount = function() {
    var self = this;
    var leaves = self._getLeaves(self.root);
    return leaves.reduce(function(sum, node) {
        return node.count + sum;
    }, 0);
};


// Helper get localStorage size
window.ls = function() {
    return Object.keys(localStorage).reduce(function(sum, key) {
        return localStorage[key].length + sum
    }, 0);
}

console.log("Initilizing ... (wait for request to complete");

//Nigeria
var nlat = 8;
var wlng = -8;
var slat = -22;
var elng = 40;

// NYC
//var nlat = 85; 
//var wlng = -72;
//var slat = -85
//var elng = -74;

// World
//var nlat = 85;
//var wlng = -180;
//var slat = -85;
//var elng = 180;

localStorage.clear();
var tree = new facilityTree(nlat, wlng, slat, elng);

setTimeout(function() {
    updateStats(tree, [[nlat, wlng], [slat, elng]]);
}, 5000);

window.tree;


var nyc = {lat: 40.80690, lng:-73.96536}
window.nyc;

//tree.getCompressedSize() / 1048576
//tree.getNNearestFacilities(7.353078, 5.118915, 500, 10)
//tree.getNNearestFacilities(40.80690, -73.96536, 500, 10)
//tree.getCompressedSize()/tree.getUncompressedSize()
//tree.getRNodesRad(40.80690, -73.96536, 500)

