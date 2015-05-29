window.l = [];
var facilityTree = function(nlat, wlng, slat, elng, countThresh, distThresh) {
    // Ajax request made below node definition
    var self = this;
    this.nlat = nlat;
    this.wlng = wlng;
    this.slat = slat;
    this.elng = elng;
    this.countThresh = countThresh;
    this.distThresh = distThresh;

    var facilityNode = function(obj) {
        
        // Bounding Box
        this.nlat = obj.nlat;
        this.wlng = obj.wlng;
        this.slat = obj.slat;
        this.elng = obj.elng;
        this.count = obj.count;// revisit query
        this.center = obj.center;
        this.latSep = Math.abs(this.center.lat - nlat);
        this.lngSep = Math.abs(this.center.lng - wlng);

        // Stats
        this.uncompressedSize = obj.uncompressedSize || 0;
        this.compressedSize = obj.compressedSize || 0;
        this.level = obj.level;

        if (!window.l[this.level]) 
            console.log("level:", this.level);

        // Data
        this.hasData = obj.data ? true : false; 
        if (this.hasData)
            this.setFacilities(obj.data);
    
        // Children
        if (obj.children) {
            if (obj.children.length > 0)
                this.nw = new facilityNode(obj.children[0]);
            if (obj.children.length > 1)
                this.ne = new facilityNode(obj.children[1]);
            if (obj.children.length > 2)
                this.sw = new facilityNode(obj.children[2]);
            if (obj.children.length > 3)
                this.se = new facilityNode(obj.children[3]);
        }
    
    };

    facilityNode.prototype.print = function(indent) {
        var indent = indent || "";
        var shift = "--";
    
        console.log(indent + " Node: " + this.center.lat, this.center.lng, this.count);
        if (this.nw && this.nw.count) { 
            console.log(indent + shift + " NW");
            this.nw.print(indent + shift)
        }
    
        if (this.ne && this.ne.count) { 
            console.log(indent + shift + " NE");
            this.ne.print(indent + shift)
        }
    
        if (this.sw && this.sw.count) { 
            console.log(indent + shift + " SW");
            this.sw.print(indent + shift)
        }
    
        if (this.se && this.se.count)  {
            console.log(indent + shift + " SE");
            this.se.print(indent + shift)
        }
    
        console.log(indent + "__");
    };
    
    facilityNode.prototype.setFacilities = function(facilities) {
        localStorage.setItem(this.nlat+""+this.wlng+""+this.slat+""+this.elng, facilities);
    };
    
    facilityNode.prototype.getFacilities = function() {
        return JSON.parse(LZString.decompressFromUTF16(localStorage[this.nlat+""+this.wlng+""+this.slat+""+this.elng]));
    };

    facilityNode.prototype.within = function(lat, lng) {
        var self = this;
        return (lat < self.nlat && lat >= self.slat && lng > self.wlng && lng <= self.elng);
    }

    facilityNode.prototype.crossesBound = function(nlat, wlng, slat, elng) {
        var self = this;

        if ((nlat < self.slat) || (slat > self.nlat))
            return false;
        
        if ((wlng > self.elng) || (elng < self.wlng))
           return false;
        
        return true;
    }

    facilityNode.prototype.distance = function(lat, lng) {
        var self = this;
        var R = 6371000; // metres
        var e = self.center.lat * Math.PI/180;
        var f = lat * Math.PI/180;
        var g = (lat - self.center.lat) * Math.PI/180;
        var h = (lng - self.center.lng) * Math.PI/180;

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
            compress: 'anything can be here',
            threshold: self.countThresh,
            seperation: self.distThresh,
            //fields: "name,uuid,coordinates,properties:sector", 
        },
        success: function(data) {
            console.log("Recieved Data traversing");
            self.total = data.total;
            self.root = new facilityNode(data.facilities[0]); 
        },
        error: function(data) {
            console.log("Done");
        },
    });

}

facilityTree.prototype._getNNode = function(lat, lng, node) {
    var self = this;

    // Maybe I'm a leaf?
    if (node.hasData) { 
        return node;
    }

    if (node.count > 0) {
        // NW
        if (node.nw && node.nw.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.nw);
            if (cnode) 
                return cnode;
        }

        // NE
        if (node.ne && node.ne.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.ne);
            if (cnode) 
                return cnode;
        }

        // SW
        if (node.sw && node.sw.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.sw);
            if (cnode) 
                return cnode;
        }

        // SE
        if (node.se && node.se.within(lat, lng)) {
            var cnode = self._getNNode(lat, lng, node.se);
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
    console.log('node: ', node.center.lat, node.center.lng, "distance from center", node.distance(lat,lng));

    return node;
}

facilityTree.prototype._getRNodes = function(nlat, wlng, slat, elng, node) {
    var self = this;

    // Maybe I'm a leaf?
    if (node.hasData) { 
        return [node]
    }

    var nodes = [];
    if (node.count > 0) {
        // NW
        if (node.nw && node.nw.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.nw));
        }

        // NE
        if (node.ne && node.ne.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.ne));
        }

        // SW
        if (node.sw && node.sw.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.sw));
        }

        // SE
        if (node.se && node.se.crossesBound(nlat, wlng, slat, elng)) {
            nodes = nodes.concat(self._getRNodes(nlat, wlng, slat, elng, node.se));
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
    if (!node.nw && !node.ne && !node.sw && !node.se) 
        return [node];

    // Otherwise check all children
    var nodes = [];
    if (node.count > 0) {
        // NW
        if (node.nw) 
            nodes = nodes.concat(self._getLeaves(node.nw));

        // NE
        if (node.ne) 
            nodes = nodes.concat(self._getLeaves(node.ne));

        // SW
        if (node.sw) 
            nodes = nodes.concat(self._getLeaves(node.sw));

        // SE
        if (node.se) 
            nodes = nodes.concat(self._getLeaves(node.se));
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
        return localStorage[key].length * 2 + sum
    }, 0);
}

console.log("Initilizing ... (wait for request to complete");
//var tree = new facilityTree(90, -180, 0, 0, 50, 0);
var tree = new facilityTree(85, -180, -85, 180, 5000, 0.000001);
window.tree;


var nyc = {lat: 40.80690, lng:-73.96536}
window.nyc;

//tree.getCompressedSize() / 1048576
//tree.getNNearestFacilities(7.353078, 5.118915, 500, 10)
//tree.getNNearestFacilities(40.80690, -73.96536, 500, 10)
//tree.getCompressedSize()/tree.getUncompressedSize()
//tree.getRNodesRad(40.80690, -73.96536, 500)

