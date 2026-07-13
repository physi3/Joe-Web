export let awardOwner, awardName, awardSlug;

export function initAwardData(){
    let awardData = document.getElementById("award-data");

    awardOwner = awardData.dataset.awardOwner;
    awardName = awardData.dataset.awardName;
    awardSlug = awardData.dataset.awardSlug;
}