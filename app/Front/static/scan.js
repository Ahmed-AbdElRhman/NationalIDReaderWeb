document.addEventListener('DOMContentLoaded', function () {
    Dynamsoft.WebTwainEnv.Containers = [{ ContainerId: 'dwtcontrolContainer', Width: 400, Height: 500 }];
    Dynamsoft.WebTwainEnv.ProductKey = 'f0068NQAAAN5kpjXn/PASaNwnk/vqnHDZY1ImTHm2SaLVmPnvSGsdsmRsNZz9GgjaAvmMkl/jye68RcbyYIVgty4MdmZfLvw=;f0068NQAAAF9P19JZGVTyVGCPlrFYlih+xSxi3A7HyTYrKA1mOlwsyqIiIxdjb2kAxSfvBxzR4A8DQdfTqVoWMMZlScXLKz4=';
    Dynamsoft.WebTwainEnv.Trial = false;
    Dynamsoft.WebTwainEnv.ResourcesPath = 'Resources';
    Dynamsoft.WebTwainEnv.AutoLoad = true;

    const scannerList = document.getElementById('scannerBTN');

    scannerList.addEventListener('click', () => {
        console.log("Hi SCan")
        AcquireImage();
    });

    var DWObject;
    var docType = Dynamsoft.EnumDWT_ImageType.IT_PDF;
    function Dynamsoft_OnReady() {
        DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
        if (DWObject) {
            DWObject.RegisterEvent('OnPostAllTransfers', function () {          // Register OnPostAllTransfers event. This event fires when all pages have been scanned and transferred
                //  document.getElementById('info').innerHTML = "The event OnPostAllTransfers is fired.";                // You can register other events here as well. Please check out 'Handling Events' in Developer's Guide
                try {
                    //alert(DWObject.GetImageURL(0,200,200));
                    //alert(createImageBase64());

                    createImageBase64();

                    DWObject.RemoveAllImages();

                }
                catch (err) {
                    alert(err.message);
                }

            });

        }
    }
    function Dynamsoft_OnPostTransfer() {
        updateLargeViewer();
    }
    function Dynamsoft_OnPostLoad(path, name, type) {
        updateLargeViewer();
    }
    function Dynamsoft_OnMouseClick() {
        updateLargeViewer();
    }
    function AcquireImage() {
        if (DWObject) {
            DWObject.SelectSource(function () {
                var OnAcquireImageSuccess, OnAcquireImageFailure;
                OnAcquireImageSuccess = OnAcquireImageFailure = function () {
                    DWObject.CloseSource();
                };
                DWObject.OpenSource();
                DWObject.IfDisableSourceAfterAcquire = true;
                DWObject.AcquireImage(OnAcquireImageSuccess, OnAcquireImageFailure);
            }, function () {
                console.log('SelectSource failed!');
            });
        }
    }
    function updateLargeViewer() {
        DWObject.CopyToClipboard(DWObject.CurrentImageIndexInBuffer);
        DWObjectLargeViewer.LoadDibFromClipboard();
    }

    function createImageBase64() {
        //var imageNumber = imageNumber[index] ;
        var aryIndices = [];
        for (var i = 0; i < DWObject.HowManyImagesInBuffer; i++) {
            aryIndices.push(i);
        }
        var imagevalue = DWObject.ConvertToBase64(
            aryIndices,
            docType,

            function (result, indices, type) {
                DWObject.LoadImageFromBase64Binary(
                    result.getData(0, result.getLength()),
                    type,
                    function () {
                        console.log(result._content)
                        parent.blobFile = result._content;
                        console.log('success');
                        parent.document.getElementById('imageurlid').value = result.getData(0, result.getLength());
                        console.log('add binary done');
                        //DWObject.RemoveAllImages();

                    },
                    function (errorCode, errorString) {
                        console.log(errorString);
                    }
                );
            },
            function (errorCode, errorString) {
                console.log(errorString);
            }
        );
        return imagevalue;
    }

});

