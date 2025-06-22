
const rules = [
    {
        type: "switch",
        should_connect_to: ["pc"],
        not_should_connect_to: ["false"],
        task: "disable CDP from ports of pc"
    },
    {
        type: "switch",
        should_connect_to: ["pc"],
        not_should_connect_to: ["false"],
        task: "Turn PCs ports to access mode"
    },
    {
        type: "switch",
        should_connect_to: ["pc"],
        not_should_connect_to: ["false"],
        task: "Enable port security"
    },
    {
        type: "switch",
        should_connect_to: ["pc","switch"],
        not_should_connect_to: ["false"],
        task: "change native vlan and remove all ports from it"
    },
    {
        type: "switch",
        should_connect_to: ["server"],
        not_should_connect_to: ["false"],
        task: "enable DHCP snooping and trust server port"
    },
    {
        type: "switch",
        should_connect_to: ["server"],
        not_should_connect_to: ["false"],
        task: "set dhcp rate limte"
    },
    {
        type: "pc",
        should_connect_to: ["false"],
        not_should_connect_to: ["false"],
        task: "Install antivirus software"
    },
    {
        type: "router",
        should_connect_to: ["switch"],
        not_should_connect_to: ["false"],
        task: "enable ip helper-address"
    }
];


const checkTask = (shapeId, shapeType) => {
    
    const applicableRules = rules.filter(rule => rule.type === shapeType);

    applicableRules.forEach(rule => {
        const element = graph.getCell(shapeId);

        
        const connectedElements = graph.getConnectedLinks(element, { outbound: true });
        let isConnectedTo;
        let isNotConnectedTo;
        if(rule.should_connect_to[1] != null){
            isConnectedTo = connectedElements.some(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text === rule.should_connect_to[0];
            }) && connectedElements.some(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text === rule.should_connect_to[1];
            });
        }else{
            isConnectedTo = rule.should_connect_to[0] === "false" || connectedElements.some(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text === rule.should_connect_to[0];
            });
        }
        if(rule.not_should_connect_to[1] != null){
            isNotConnectedTo =connectedElements.every(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text !== rule.not_should_connect_to[0];
            }) && connectedElements.every(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text !== rule.not_should_connect_to[1];
            });
        }else{
            isNotConnectedTo = rule.not_should_connect_to[0] === "false" || connectedElements.every(link => {
                const targetElement = graph.getCell(link.attributes.target.id);
                return targetElement.attributes.attrs.label.text !== rule.not_should_connect_to;
            });
        }

        
        if (isConnectedTo && isNotConnectedTo) {
            
            const tasks = JSON.parse(localStorage.getItem(shapeId)) || [];

            
            const taskExists = tasks.some(task => task.text === rule.task);

            if (!taskExists) {
                
                tasks.push({ text: rule.task, checked: false });
                localStorage.setItem(shapeId, JSON.stringify(tasks));
            }
        }
    });
};